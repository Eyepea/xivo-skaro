# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2010 Proformatique'
__author__    = 'Corentin Le Gall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Directory search related definitions.

Here's the list of standardized keys, i.e. identifiers that can be used in
display format strings and that should be mapped by directories:
  firstname -- the first name
  lastname -- the last name
  mail -- the electronic mail address
  phone -- the phone number
  society -- the society name
  fullname -- the display name
  reverse -- used for reverse lookup

"""

import csv
import logging
import re
import urllib
import urllib2
from itertools import chain, ifilter, imap, izip
from operator import itemgetter
from xivo_ctiservers import db_connection_manager
from xivo_ctiservers import xivo_ldap

log = logging.getLogger('directories')

# XXX str/unicode is handled the same way as in 1.1, it might need to be
#     reviewed more carefully since it seems a bit inconsistent/incomplete
# XXX there is a potential problem for reverse lookup since it doesn't do
#     exact string matching, so if we lookup for number '0' then we'll return
#     every entry that has a '0' in it, which is not what we want. That said,
#     this behaviour was the same in 1.1 for most directory src


class Context(object):
    def __init__(self, directories, display, didextens):
        """
        directories -- a list of directory objects to use for direct lookup
        display -- a display object to format the results of direct lookup
        didextens -- a dictionary mapping extension number to list of
          directory objects for reverse lookup
        """
        self._directories = directories
        self._display = display
        self._didextens = didextens
    
    def lookup_direct(self, string):
        """Return a tuple (<headers>, <resultlist>)."""
        if self._display is None:
            raise Exception('No display defined for this context')
        directory_results = []
        for directory in self._directories:
            log.info('Direct lookup in directory %s', directory.name)
            try:
                directory_result = directory.lookup_direct(string)
            except Exception:
                log.error('Error while looking up in directory %s for %s',
                          directory.name, string, exc_info=True)
            else:
                directory_results.append(directory_result)
        combined_results = chain.from_iterable(directory_results)
        resultlist = list(self._display.format(combined_results))
        return self._display.display_header, resultlist
    
    def lookup_reverse(self, did_number, number):
        """Return a list of directory entries."""
        if did_number in self._didextens:
            directories = self._didextens[did_number]
        elif '*' in self._didextens:
            directories = self._didextens['*']
        else:
            log.warning('No directories for DID %s', did_number)
            return []
        
        directory_results = []
        for directory in directories:
            log.info('Reverse lookup in directory %s', directory.name)
            try:
                directory_result = directory.lookup_reverse(number)
            except Exception:
                log.error('Error while looking up in directory %s for %s',
                          directory.name, number, exc_info=True)
            else:
                directory_results.append(directory_result)
        combined_results = list(chain.from_iterable(directory_results))
        return combined_results
    
    @classmethod
    def new_from_contents(cls, avail_displays, avail_directories, contents):
        """Return a new instance of this class from "configuration contents"
        and dictionaries of displays and directories object.
        
        """ 
        directories = cls._directories_from_contents(avail_directories, contents)
        display = cls._display_from_contents(avail_displays, contents)
        didextens = cls._didextens_from_contents(avail_directories, contents)
        return cls(directories, display, didextens)
    
    @staticmethod
    def _directories_from_contents(avail_directories, contents):
        directory_ids = contents.get('directories', [])
        directories = [avail_directories[directory_id] for directory_id in
                       directory_ids]
        return directories
    
    @staticmethod
    def _display_from_contents(avail_displays, contents):
        display_id = contents.get('display')
        return avail_displays.get(display_id)
    
    @staticmethod
    def _didextens_from_contents(avail_directories, contents):
        raw_didextens = contents.get('didextens', {})
        didextens = {}
        for exten, directory_ids in raw_didextens.iteritems():
            directories = [avail_directories[directory_id] for directory_id in
                           directory_ids]
            didextens[exten] = directories
        return didextens


_APPLY_SUBS_REGEX = re.compile(r'\{([^}]+)\}')

def _apply_subs(display_elem, result):
    fmt_string = display_elem['fmt']
    # use of 1-element list since we can't rebind local variables in inner scope
    # in python2
    nb_subs = [0]
    nb_succesfull_subs = [0]
    def aux(m):
        nb_subs[0] += 1
        var_name = m.group(1)
        if var_name in result:
            nb_succesfull_subs[0] += 1
            return result[var_name]
        else:
            return m.group()
    fmted_string = _APPLY_SUBS_REGEX.sub(aux, fmt_string)
    # use default value if there was at least one substitution tried
    # but none were successful
    if nb_subs[0] > 0 and nb_succesfull_subs[0] == 0:
        fmted_string = display_elem.get('default', '')
    return fmted_string


class Display(object):
    def __init__(self, display_elems):
        """
        display_elems -- a list of dictionaries with the followings keys:
          'title', 'default' and 'fmt'.
        """
        self._display_elems = display_elems
        self.display_header = [e['title'] for e in display_elems]
        self._map_fun = self._new_map_function()
    
    def format(self, results):
        """Return an iterator over the formated results."""
        return imap(self._map_fun, results)
    
    def _new_map_function(self):
        def aux(result):
            return ';'.join(_apply_subs(display_elem, result) for
                            display_elem in self._display_elems)
        return aux
    
    @classmethod
    def new_from_contents(cls, contents):
        # Example contents:
        #   [{"title": "Numero",
        #     "default": "",
        #     "fmt": "{db-phone}"},
        #    {"title":"Nom",
        #     "default": "",
        #     "fmt": "{db-fullname}"
        #    }]
        # XXX in fact, we are still expecting that contents be the old format
        contents = list({'title': v[0], 'default': v[2], 'fmt': v[3]} for
                        (_, v) in
                        sorted(contents.iteritems(), key=itemgetter(0)))
        return cls(contents)


def _get_key_mapping(contents):
    # Return a dictionary mapping std key to src key
    key_mapping = {}
    for k, v in contents.iteritems():
        if k.startswith('field_'):
            # strip the leading 'field_' and add a leading 'db-'
            std_key = 'db-' + k[6:]
            # XXX right now we only handle 1 src key per std key
            key_mapping[std_key] = v[0]
    return key_mapping


class CSVFileDirectoryDataSource(object):
    def __init__(self, csv_file, delimiter, key_mapping):
        """
        csv_file -- the path to the CSV file
        delimiter -- the character used to separate fields in the CSV file
        key_mapping -- a dictionary mapping std key to list of CSV field name
        """
        log.debug('New directory data source %s', self.__class__.__name__)
        self._csv_file = csv_file
        self._delimiter = delimiter
        self._key_mapping = key_mapping
    
    def lookup(self, string, fields):
        """Do a lookup using string to match on the given list of src fields."""
        encoded_string = string.encode('UTF-8')
        fobj = urllib2.urlopen(self._csv_file)
        try:
            reader = csv.DictReader(fobj, delimiter=self._delimiter)
            filter_fun = self._new_filter_function(encoded_string, fields,
                                                   reader.fieldnames)
            map_fun = self._new_map_function(reader.fieldnames)
            def generator():
                try:
                    for result in imap(map_fun, ifilter(filter_fun, reader)):
                        yield result
                finally:
                    fobj.close()
            # this function is not an iterator because we want the fail fast
            # behaviour that iterator/generator doesn't have
            return generator()
        except Exception:
            fobj.close()
            raise
    
    def _new_filter_function(self, string, requested_fields, available_fields):
        lookup_fields = list(set(available_fields).intersection(requested_fields))
        if not lookup_fields:
            log.warning('Requested fields %s but only fields %s are available',
                        requested_fields, available_fields)
        lowered_string = string.lower()
        def aux(row):
            for field in lookup_fields:
                if lowered_string in row[field].lower():
                    return True
            return False
        return aux
    
    def _new_map_function(self, available_fields):
        mapping = list((std_key, src_key) for
                       (std_key, src_key) in self._key_mapping.iteritems() if
                       src_key in available_fields)
        if not mapping:
            log.warning('Key mapping %s but only fields %s are available',
                        self._key_mapping, available_fields)
        def aux(row):
            return dict((std_key, row[src_key]) for (std_key, src_key) in mapping)
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        """Return a new instance of this class from "configuration contents"
        and a ctiserver instance.
        
        """
        csv_file = contents['uri']
        delimiter = contents.get('delimiter', ',')
        key_mapping = _get_key_mapping(contents)
        return cls(csv_file, delimiter, key_mapping)


class SQLDirectoryDataSource(object):
    def __init__(self, db_uri, key_mapping):
        log.debug('New directory data source %s', self.__class__.__name__)
        self._db_uri = db_uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()
    
    def lookup(self, string, fields):
        # handle when fields is empty to simplify implementation
        if not fields:
            log.warning('No requested fields')
            return []
        
        table, test_columns = self._get_table_and_columns_from_fields(fields)
        request_beg = 'SELECT ${columns} FROM %s WHERE ' % table
        request_end = ' OR '.join('%s LIKE %%s' % column for column in test_columns)
        request = request_beg + request_end
        params = ('%' + string + '%',) * len(test_columns)
        columns = tuple(self._key_mapping.itervalues())
        
        conn_mgr = db_connection_manager.DbConnectionPool(self._db_uri)
        connection = conn_mgr.get()
        try:
            cursor = connection['cur']
            log.debug('Doing SQL request: %s', request)
            cursor.query(request, columns, params)
            def generator():
                try:
                    while True:
                        row = cursor.fetchone()
                        if row is None:
                            break
                        yield self._map_fun(row)
                finally:
                    conn_mgr.put()
            return generator()
        except Exception:
            conn_mgr.put()
            raise
    
    def _get_table_and_columns_from_fields(self, fields):
        # Return a tuple (table id, list of column ids)
        tables = set()
        columns = set()
        for field in fields:
            table, column = field.split('.', 1)
            tables.add(table)
            columns.add(column)
        if len(tables) != 1:
            raise ValueError('fields must reference exactly 1 table: %s' % tables)
        return tables.pop(), list(columns)
    
    def _new_map_fun(self):
        def aux(row):
            return dict(izip(self._key_mapping, row))
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        db_uri = contents['uri']
        key_mapping = _get_key_mapping(contents)
        return cls(db_uri, key_mapping)


class InternalDirectoryDataSource(object):
    def __init__(self, db_uri, key_mapping):
        log.debug('New directory data source %s', self.__class__.__name__)
        self._db_uri = db_uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()
    
    def lookup(self, string, fields):
        # handle when fields is empty to simplify implementation
        if not fields:
            log.warning('No requested fields')
            return []

        test_columns = fields
        request_beg = 'SELECT ${columns} FROM userfeatures ' \
                'LEFT JOIN linefeatures ON userfeatures.id = linefeatures.iduserfeatures ' \
                'WHERE '
        request_end = ' OR '.join('%s LIKE %%s' % column for column in test_columns)
        request = request_beg + request_end
        params = ('%' + string + '%',) * len(test_columns)
        columns = tuple(self._key_mapping.itervalues())
        
        conn_mgr = db_connection_manager.DbConnectionPool(self._db_uri)
        connection = conn_mgr.get()
        try:
            cursor = connection['cur']
            log.debug('Doing SQL request: %s', request)
            cursor.query(request, columns, params)
            def generator():
                try:
                    while True:
                        row = cursor.fetchone()
                        if row is None:
                            break
                        yield self._map_fun(row)
                finally:
                    conn_mgr.put()
            return generator()
        except Exception:
            conn_mgr.put()
            raise
    
    def _new_map_fun(self):
        def aux(row):
            return dict(izip(self._key_mapping, row))
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        db_uri = ctid.cconf.getconfig('ipbxes')[ctid.myipbxid]['userfeatures_db_uri']
        key_mapping = _get_key_mapping(contents)
        return cls(db_uri, key_mapping)


class LDAPDirectoryDataSource(object):
    def __init__(self, uri, key_mapping):
        log.debug('New directory data source %s', self.__class__.__name__)
        self._uri = uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()
        self._xivo_ldap = None
    
    def lookup(self, string, fields):
        ldap_filter = ['(%s=*%s*)' % (field, string) for field in fields]
        ldap_attributes = []
        for src_key in self._key_mapping.itervalues():
            if isinstance(src_key, unicode):
                ldap_attributes.append(src_key.encode('UTF-8'))
            else:
                ldap_attributes.append(src_key)
        ldapid = self._try_connect()
        if ldapid.ldapobj is not None:
            try:
                results = ldapid.getldap('(|%s)' % ''.join(ldap_filter),
                                         ldap_attributes, string)
            except Exception, e:
                log.warning('Error with LDAP request: %s', e)
                self._xivo_ldap = None
            else:
                if results is not None:
                    return imap(self._map_fun, results)
        return []
    
    def _try_connect(self):
        # Try to connect/reconnect to the LDAP if necessary
        if self._xivo_ldap is None:
            ldapid = xivo_ldap.xivo_ldap(self._uri)
            if ldapid.ldapobj is not None:
                self._xivo_ldap = ldapid
        else:
            ldapid = self._xivo_ldap
            if ldapid.ldapobj is None:
                self._xivo_ldap = None
        return ldapid
    
    def _new_map_fun(self):
        def aux(ldap_result):
            return dict((std_key, ldap_result[1][src_key][0]) for
                        (std_key, src_key) in self._key_mapping.iteritems() if
                        src_key in ldap_result[1])
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        uri = contents['uri']
        key_mapping = _get_key_mapping(contents)
        return cls(uri, key_mapping)


class HTTPDirectoryDataSource(object):
    def __init__(self, base_uri, delimiter, key_mapping):
        log.debug('New directory data source %s', self.__class__.__name__)
        self._base_uri = base_uri
        self._delimiter = delimiter
        self._key_mapping = key_mapping
    
    def lookup(self, string, fields):
        uri = self._build_uri(string, fields)
        fobj = urllib2.urlopen(uri)
        try:
            charset = self._get_result_charset(fobj)
            try:
                line = fobj.next()
            except StopIteration:
                raise ValueError('no lines in result from %s', uri)
            else:
                line = line.decode(charset).rstrip()
                headers = line.split(self._delimiter)
                map_fun = self._new_map_function(headers, charset)
                def generator():
                    try:
                        for result in imap(map_fun, fobj):
                            yield result
                    finally:
                        fobj.close()
                return generator()
        except Exception:
            fobj.close()
            raise
    
    def _build_uri(self, string, fields):
        uri = self._base_uri
        if uri[8:].find('/') == -1:
            uri += '/'
        encoded_string = urllib.quote(string.encode('UTF-8'))
        uri += '?' + '&'.join(field + '=' + encoded_string for field in fields)
        return uri
    
    def _get_result_charset(self, fobj):
        charset = 'UTF-8'
        content_type = fobj.info().getheader('Content-Type')
        if content_type:
            i = content_type.lower().find('charset=')
            if i >= 0:
                charset = content_type[i:].split(' ', 1)[0].split('=', 1)[1]
        return charset
    
    def _new_map_function(self, headers, charset):
        headers_map = dict((header, idx) for (idx, header) in enumerate(headers))
        mapping = [(std_key, headers_map[src_key]) for (std_key, src_key) in
                   self._key_mapping.iteritems() if
                   src_key in headers_map]
        def aux(line):
            line = line.decode(charset).rstrip()
            tokens = line.split(self._delimiter)
            return dict((std_key, tokens[idx]) for (std_key, idx) in mapping)
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        base_uri = contents['uri']
        delimiter = contents.get('delimiter', ',')
        key_mapping = _get_key_mapping(contents)
        return cls(base_uri, delimiter, key_mapping)


class PhonebookDirectoryDataSource(object):
    def __init__(self, phonebook_list, key_mapping):
        log.debug('New directory data source %s', self.__class__.__name__)
        self._phonebook_list = phonebook_list
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_function()
    
    def lookup(self, string, fields):
        filter_fun = self._new_filter_function(string, fields)
        return imap(self._map_fun, ifilter(filter_fun,
                                           self._phonebook_list.keeplist.itervalues()))
    
    def _new_filter_function(self, string, fields):
        lowered_string = string.lower()
        def aux(phonebook_entry):
            for field in fields:
                if field in phonebook_entry:
                    if lowered_string in phonebook_entry[field].lower():
                        return True
            return False
        return aux
    
    def _new_map_function(self):
        def aux(phonebook_entry):
            return dict((std_key, phonebook_entry[src_key]) for (std_key, src_key) in
                        self._key_mapping.iteritems() if
                        src_key in phonebook_entry)
        return aux
    
    @classmethod
    def new_from_contents(cls, ctid, contents):
        phonebook_list = ctid.safe[ctid.myipbxid].xod_config['phonebooks']
        key_mapping = _get_key_mapping(contents)
        return cls(phonebook_list, key_mapping)


class DirectoryAdapter(object):
    """Adapt a DirectoryDataSource instance to the Directory interface,
    i.e. to something with a name attribute, a lookup_direct and
    lookup_reverse method, etc...
    
    """
    def __init__(self, directory_src, name, match_direct, match_reverse):
        self._directory_src = directory_src
        self.name = name
        self._match_direct = match_direct
        self._match_reverse = match_reverse
        self._map_fun = self._new_map_function()
    
    def _new_map_function(self):
        def aux(result):
            result['xivo-directory'] = self.name
            return result
        return aux
    
    def lookup_direct(self, string):
        return imap(self._map_fun, self._directory_src.lookup(string, self._match_direct))
    
    def lookup_reverse(self, string):
        return self._directory_src.lookup(string, self._match_reverse)
    
    @classmethod
    def new_from_contents(cls, directory, contents):
        name = contents['name']
        match_direct = contents['match_direct']
        match_reverse = contents['match_reverse']
        return cls(directory, name, match_direct, match_reverse)


class ContextsMgr(object):
    def __init__(self):
        self.contexts = {}
        self._old_contents = {}
    
    def update(self, avail_displays, avail_directories, contents):
        log.debug('Updating contexts in manager')
        # remove old contexts
        # deleting a key will raise a RuntimeError if you do not use .keys() here
        for context_id in self.contexts.keys():
            if context_id not in contents:
                log.info('Removing context %s', context_id)
                del self.contexts[context_id]
        # add/update contexts
        for context_id, context_contents in contents.iteritems():
            if context_contents != self._old_contents.get(context_id):
                log.info('Adding/updating context %s', context_id)
                try:
                    self.contexts[context_id] = Context.new_from_contents(
                            avail_displays, avail_directories, context_contents)
                except Exception:
                    log.error('Error while creating context %s from %s',
                              context_id, context_contents, exc_info=True)
        self._old_contents = contents


class DisplaysMgr(object):
    def __init__(self):
        self.displays = {}
        self._old_contents = {}
    
    def update(self, contents):
        log.debug('Updating displays in manager')
        # remove old displays
        # deleting a key will raise a RuntimeError if you do not use .keys() here
        for display_id in self.displays.keys():
            if display_id not in contents:
                log.info('Removing display %s', display_id)
                del self.displays[display_id]
        # add/update displays
        for display_id, display_contents in contents.iteritems():
            if display_contents != self._old_contents.get(display_id):
                log.info('Adding/updating display %s', display_id)
                try:
                    self.displays[display_id] = Display.new_from_contents(display_contents)
                except Exception:
                    log.error('Error while creating display %s from %s',
                              display_id, display_contents, exc_info=True)
        self._old_contents = contents


class DirectoriesMgr(object):
    _DIRECTORY_SRC_CLASSES = {
        'file': CSVFileDirectoryDataSource,
        'http': HTTPDirectoryDataSource,
        'internal': InternalDirectoryDataSource,
        'ldap': LDAPDirectoryDataSource,
        'ldaps': LDAPDirectoryDataSource,
        'phonebook': PhonebookDirectoryDataSource,
        'sqlite': SQLDirectoryDataSource,
        'mysql': SQLDirectoryDataSource,
        'postgresql': SQLDirectoryDataSource,
    }
    
    def __init__(self):
        self.directories = {}
        self._old_contents = {}
    
    def update(self, ctid, contents):
        log.debug('Updating directories in manager')
        # remove old directories
        # deleting a key will raise a RuntimeError if you do not use .keys() here
        for directory_id in self.directories.keys():
            if directory_id not in contents:
                log.info('Removing directory %s', directory_id)
                del self.directories[directory_id]
        # add/update directories
        for directory_id, directory_contents in contents.iteritems():
            if directory_contents != self._old_contents.get(directory_id):
                log.info('Adding/updating directory %s', directory_id)
                try:
                    class_ = self._get_directory_class(directory_contents)
                    directory_src = class_.new_from_contents(ctid, directory_contents)
                    directory = DirectoryAdapter.new_from_contents(directory_src, directory_contents)
                    self.directories[directory_id] = directory
                except Exception:
                    log.error('Error while creating directory %s from %s',
                              directory_id, directory_contents, exc_info=True)
        self._old_contents = contents
    
    def _get_directory_class(self, directory_contents):
        uri = directory_contents['uri']
        kind = uri.split(':', 1)[0]
        return self._DIRECTORY_SRC_CLASSES[kind]
