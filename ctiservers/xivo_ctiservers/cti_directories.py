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
"""

import logging
import urllib
from xivo import anysql
from xivo.BackSQL import backmysql
from xivo.BackSQL import backsqlite
from xivo_ctiservers import xivo_ldap
from xivo_ctiservers import cti_directories_csv

log = logging.getLogger('directories')

class Context:
    def __init__(self):
        self.directories = list()
        self.display = None
        self.didextens = dict()
        return

    def update(self, contents):
        self.directories = list()
        if 'directories' in contents:
            directories = contents.get('directories')
            for direct in directories:
                dtr = direct[12:]
                if dtr not in self.directories:
                    self.directories.append(dtr)
        self.display = contents.get('display')
        self.didextens = contents.get('didextens')
        return

class Display:
    def __init__(self):
        self.display_header = []
        self.outputformat = ''
        return

    def update(self, contents):
        display_items = contents.keys()
        display_items.sort()
        self.outputformat = ''
        fmt = []
        self.display_header = []
        for k in display_items:
            [title, type, defaultval, format] = contents.get(k)
            self.display_header.append(title)
            fmt.append(format)
        self.outputformat = ';'.join(fmt)
        # XXX make a csv output instead
        # XXX handle type ? handle defaultval ?
        return

class Directory:
    def __init__(self, dirid):
        self.dirid = dirid
        self.uri = ''
        self.name = '(noname)'

        self.display_reverse = '{db-fullname}'
        self.match_direct = []
        self.match_reverse = []

        self.delimiter = ';'
        self.sqltable = 'UNDEFINED'
        return

    def update(self, xivoconf_local):
        self.fkeys = {}
        for field, value in xivoconf_local.iteritems():
            if field.startswith('field_'):
                keyword = field.split('_')[1]
                self.fkeys['db-%s' % keyword] = value
            elif field in 'uri':
                self.dbkind = value.split(':')[0]
                self.uri = value
                if self.dbkind.find('sql') >= 0:
                    if value.find('?table=') > 0:
                        self.uri = value.split('?table=')[0]
                        self.sqltable = value.split('?table=')[1]
            elif field == 'name':
                self.name = value
            elif field == 'delimiter':
                self.delimiter = value
            elif field == 'display_reverse':
                if value:
                    self.display_reverse = value[0]
            elif field == 'match_direct':
                self.match_direct = value
            elif field == 'match_reverse':
                self.match_reverse = value
        return

# - '*' (wildcard) support
# - more than 1 result
# - message for error/empty
# - encodings
# - avoid reconnections to already opened links (if applicable)
# - better reverse vs. direct
# - extend to 'internal'

    def findpattern(self, searchpattern, reversedir):
        fullstatlist = []

        if searchpattern == '':
            return []

        if self.dbkind in ['ldap', 'ldaps']:
            ldap_filter = []
            ldap_attributes = []
            for fname in self.match_direct:
                if searchpattern == '*':
                    ldap_filter.append("(%s=*)" % fname)
                else:
                    ldap_filter.append("(%s=*%s*)" %(fname, searchpattern))

            for listvalue in self.fkeys.itervalues():
                for attrib in listvalue:
                    if isinstance(attrib, unicode):
                        ldap_attributes.append(attrib.encode('utf8'))
                    else:
                        ldap_attributes.append(attrib)

            try:
                results = None
                if self.uri not in xivocti.ldapids:
                    # first connection to ldap, or after failure
                    ldapid = xivo_ldap.xivo_ldap(self.uri)
                    if ldapid.ldapobj is not None:
                        xivocti.ldapids[self.uri] = ldapid
                else:
                    # retrieve the connection already setup, if not yet deleted
                    ldapid = xivocti.ldapids[self.uri]
                    if ldapid.ldapobj is None:
                        del xivocti.ldapids[self.uri]

                # at this point, either we have a successful ldapid.ldapobj value, with xivocti.ldapids[self.uri] = ldapid
                #                either ldapid.ldapobj is None, and self.uri not in xivocti.ldapids

                if ldapid.ldapobj is not None:
                    # if the ldapid had already been defined and setup, the failure would occur here
                    try:
                        results = ldapid.getldap('(|%s)' % ''.join(ldap_filter),
                                                 ldap_attributes,
                                                 searchpattern)
                    except Exception:
                        ldapid.ldapobj = None
                        del xivocti.ldapids[self.uri]

                if results is not None:
                    for result in results:
                        futureline = {'xivo-directory' : self.name}
                        for keyw, dbkeys in self.fkeys.iteritems():
                            for dbkey in dbkeys:
                                if futureline.get(keyw, '') != '':
                                    break
                                elif dbkey in result[1]:
                                    futureline[keyw] = result[1][dbkey][0]
                                elif keyw not in futureline:
                                    futureline[keyw] = ''
                        fullstatlist.append(futureline)
            except Exception:
                log.exception('ldaprequest (directory)')

        elif self.dbkind == 'phonebook':
            if reversedir:
                matchkeywords = self.match_reverse
            else:
                matchkeywords = self.match_direct
            for iastid in xivocti.weblist['phonebook'].keys():
                for k, v in xivocti.weblist['phonebook'][iastid].keeplist.iteritems():
                    matchme = False
                    for tmatch in matchkeywords:
                        if v.has_key(tmatch):
                            if reversedir:
                                if v[tmatch].lstrip('0') == searchpattern.lstrip('0'):
                                    matchme = True
                            else:
                                if searchpattern == '*' or v[tmatch].lower().find(searchpattern.lower()) >= 0:
                                    matchme = True
                    if matchme:
                        futureline = {'xivo-directory' : self.name}
                        for keyw, dbkeys in self.fkeys.iteritems():
                            for dbkey in dbkeys:
                                if dbkey in v.keys():
                                    futureline[keyw] = v[dbkey]
                        fullstatlist.append(futureline)

        elif self.dbkind == 'file':
            if reversedir:
                matchkeywords = self.match_reverse
            else:
                matchkeywords = self.match_direct
            fullstatlist = cti_directories_csv.lookup(searchpattern.encode('utf8'),
                                                      self.uri,
                                                      matchkeywords,
                                                      self.fkeys,
                                                      self.delimiter,
                                                      self.name)

        elif self.dbkind == 'http':
            if not reversedir:
                fulluri = self.uri
                # add an ending slash if needed
                if fulluri[8:].find('/') == -1:
                    fulluri += '/'
                fulluri += '?' + '&'.join([key + '=' + urllib.quote(searchpattern.encode('utf-8')) for key in self.match_direct])
                n = 0
                try:
                    f = urllib.urlopen(fulluri)
                    # use f.info() to detect charset
                    charset = 'utf-8'
                    s = f.info().getheader('Content-Type')
                    k = s.lower().find('charset=')
                    if k >= 0:
                        charset = s[k:].split(' ')[0].split('=')[1]                                    
                    for line in f:
                        if n == 0:
                            header = line
                            headerfields = header.strip().split(self.delimiter)
                        else:
                            ll = line.strip()
                            if isinstance(ll, str): # dont try to decode unicode string.
                                ll = ll.decode(charset)
                            t = ll.split(self.delimiter)
                            futureline = {'xivo-directory' : self.name}
                            # XXX problem when badly set delimiter + index()
                            for keyw, dbkeys in self.fkeys.iteritems():
                                for dbkey in dbkeys:
                                    idx = headerfields.index(dbkey)
                                    futureline[keyw] = t[idx]
                            fullstatlist.append(futureline)
                        n += 1
                    f.close()
                except Exception:
                    log.exception('__build_customers_bydirdef__ (http) %s' % fulluri)
                if n == 0:
                    log.warning('WARNING : %s is empty' % self.uri)
                # we don't warn about "only one line" here since the filter has probably already been applied
            else:
                fulluri = self.uri
                # add an ending slash if needed
                if fulluri[8:].find('/') == -1:
                    fulluri += '/'
                fulluri += '?' + '&'.join([key + '=' + urllib.quote(searchpattern) for key in self.match_reverse])
                f = urllib.urlopen(fulluri)
                # TODO : use f.info() to detect charset
                fsl = f.read().strip()
                if fsl:
                    fullstatlist = [ {'xivo-directory' : self.name,
                                      'db-fullname' : fsl}]
                else:
                    fullstatlist = []

        elif self.dbkind in ['sqlite', 'mysql']:
            if searchpattern == '*':
                whereline = ''
            else:
                # prevent SQL injection and make use of '*' wildcard possible
                esc_searchpattern = searchpattern.replace("'", "\\'").replace('%', '\\%').replace('*', '%')
                wl = ["%s LIKE '%%%s%%'" % (fname, esc_searchpattern) for fname in self.match_direct]
                whereline = 'WHERE ' + ' OR '.join(wl)

            results = []
            try:
                conn = anysql.connect_by_uri(str(self.uri))
                cursor = conn.cursor()
                sqlrequest = 'SELECT ${columns} FROM %s %s' % (self.sqltable, whereline)
                cursor.query(sqlrequest,
                             tuple(self.match_direct),
                             None)
                results = cursor.fetchall()
                conn.close()
            except Exception:
                log.exception('sqlrequest for %s' % self.uri)

            for result in results:
                futureline = {'xivo-directory' : self.name}
                for keyw, dbkeys in self.fkeys.iteritems():
                    for dbkey in dbkeys:
                        if dbkey in self.match_direct:
                            n = self.match_direct.index(dbkey)
                            futureline[keyw] = result[n]
                fullstatlist.append(futureline)

        elif self.dbkind in ['internal']:
            pass

        elif self.dbkind in ['mssql']:
            pass

        else:
            log.warning('wrong or no database method defined (%s) - please fill the uri field of the directory <%s> definition'
                        % (self.dbkind, self.dirid))



        if reversedir:
            display_reverse = self.display_reverse
            if fullstatlist:
                for k, v in fullstatlist[0].iteritems():
                    if isinstance(v, unicode):
                        display_reverse = display_reverse.replace('{%s}' % k, v)
                    elif isinstance(v, str):
                        # decoding utf8 data as we know the DB is storing utf8 so some bug may lead this data to come here still utf8 encoded
                        # in the future, this code could be removed, once we are sure encoding is properly handled "up there" (in sqlite client)
                        display_reverse = display_reverse.replace('{%s}' % k, v.decode('utf8'))
                    else:
                        log.warning('__build_customers_bydirdef__ %s is neither unicode nor str' % k)
                e = fullstatlist[0]
                e.update({'dbr-display' : display_reverse})
        return fullstatlist
