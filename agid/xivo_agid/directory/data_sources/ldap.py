# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
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

import logging
from itertools import imap
from xivo_agid.directory.data_sources.directory_data_source import DirectoryDataSource
from xivo_dird.ldap import XivoLDAP

logger = logging.getLogger('ldap directory')


class LDAPDirectoryDataSource(DirectoryDataSource):

    ldap_encoding = 'utf-8'

    def __init__(self, uri, key_mapping):
        self._uri = uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()
        self._xivo_ldap = None

    def lookup(self, search_pattern, fields, contexts=None):
        search_pattern_normalized = self._normalize_pattern(search_pattern)
        search_pattern_encoded = self._encode_search_pattern(search_pattern_normalized)
        ldap_search_filter = self._compute_ldap_search_filter(search_pattern_encoded,
                                                              fields)
        ldap_attributes_to_query = self._compute_ldap_attributes_to_query()

        ldap_results = self._query_ldap(search_pattern_encoded,
                                        ldap_search_filter,
                                        ldap_attributes_to_query)

        ldap_results_decoded = self._decode_results(ldap_results)
        return self._format_results(ldap_results_decoded)

    def _normalize_pattern(self, search_pattern):
        if search_pattern is None:
            return ''
        else:
            return search_pattern

    def _encode_search_pattern(self, search_pattern):
        return search_pattern.encode(self.ldap_encoding)

    def _compute_ldap_search_filter(self, search_pattern, fields):
        ldap_filter = ['(%s=*%s*)' % (field, search_pattern) for field in fields]
        str_ldap_filter = '(|%s)' % ''.join(ldap_filter)
        return str_ldap_filter

    def _compute_ldap_attributes_to_query(self):
        ldap_attributes = []
        for src_key in self._key_mapping.itervalues():
            if isinstance(src_key, unicode):
                ldap_attributes.append(src_key.encode(self.ldap_encoding))
            else:
                ldap_attributes.append(src_key)
        return ldap_attributes

    def _query_ldap(self,
                    search_pattern,
                    ldap_search_filter,
                    ldap_attributes_to_query):
        ldapid = self._try_connect()
        results = []
        if ldapid.ldapobj is not None:
            results = ldapid.getldap(ldap_search_filter,
                                     ldap_attributes_to_query,
                                     search_pattern)
        return results

    def _decode_results(self, ldap_results):
        decoded_results = []
        for entry in ldap_results:
            decoded_results.append(self._decode_entry(entry))
        return decoded_results

    def _format_results(self, ldap_results):
        return imap(self._map_fun, ldap_results)

    def _try_connect(self):
        # Try to connect/reconnect to the LDAP if necessary
        if self._xivo_ldap is None:
            ldapid = XivoLDAP(self._uri)
            if ldapid.ldapobj is not None:
                self._xivo_ldap = ldapid
        else:
            ldapid = self._xivo_ldap
            if ldapid.ldapobj is None:
                self._xivo_ldap = None
        return ldapid

    def _decode_entry(self, entry):
        domain_name, attributes = entry
        decoded_domain_name = domain_name.decode(self.ldap_encoding)
        decoded_attributes = self._decode_attributes(attributes)
        return (decoded_domain_name, decoded_attributes)

    def _decode_attributes(self, attributes):
        decoded_attributes = {}
        for attribute, values in attributes.iteritems():
            decoded_attribute = attribute.decode(self.ldap_encoding)
            decoded_values = self._decode_values(values)
            decoded_attributes[decoded_attribute] = decoded_values
        return decoded_attributes

    def _decode_values(self, values):
        decoded_values = []
        for value in values:
            decoded_values.append(value.decode(self.ldap_encoding))
        return decoded_values

    def _new_map_fun(self):
        def aux(ldap_result):
            return dict((std_key, ldap_result[1][src_key][0]) for
                        (std_key, src_key) in self._key_mapping.iteritems() if
                        src_key in ldap_result[1])
        return aux

    @classmethod
    def new_from_contents(cls, contents):
        uri = contents['uri']
        key_mapping = cls._get_key_mapping(contents)
        return cls(uri, key_mapping)
