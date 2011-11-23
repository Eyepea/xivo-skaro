# -*- coding: utf8 -*-
"""Backend support for PostgreSQL for anysql

Copyright (C) 2010  Avencall

"""

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2007-2010  Avencall

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import psycopg2

from xivo import anysql
from xivo import urisup
from xivo.urisup import SCHEME, AUTHORITY, PATH, QUERY, FRAGMENT, uri_help_split

__typemap = {
    "host": str,
    "user": str,
    "passwd": str,
    "db": str,
    "port": int,
    "unix_socket": str,
    "compress": bool,
    "connect_timeout": int,
    "read_default_file": str,
    "read_default_group": str,
    "use_unicode": (lambda x: bool(int(x))),
    "conv": None,
    "quote_conv": None,
    "cursorclass": None,
    "charset": str,
}

def __apply_types(params, typemap):
    for k in typemap.iterkeys():
        if k in params:
            if typemap[k] is not None:
                params[k] = typemap[k](params[k])
            else:
                del params[k]

def __dict_from_query(query):
    print "dfQ=",query
    if not query:
        return {}
    return dict(query)

def connect_by_uri(uri):
    """General URI syntax:

    postgresql://user:passwd@host:port/db

    NOTE: the authority and the path parts of the URI have precedence
    over the query part, if an argument is given in both.

        conv,quote_conv,cursorclass
    are not (yet?) allowed as complex Python objects are needed, hard to
    transmit within an URI...
    """
    puri   = urisup.uri_help_split(uri)
		#params = __dict_from_query(puri[QUERY])
    params = {}

    if puri[AUTHORITY]:
        user, passwd, host, port = puri[AUTHORITY]
        if user:
            params['user'] = user
        if passwd:
            params['password'] = passwd
        if host:
            params['host'] = host
        if port:
            params['port'] = port
    if puri[PATH]:
        params['database'] = puri[PATH]
        if params['database'] and params['database'][0] == '/':
            params['database'] = params['database'][1:]

    #__apply_types(params, __typemap)

    return psycopg2.connect(**params)

def escape(s):
    return '.'.join(['"%s"' % comp for comp in s.split('.')])

def cast(fieldname, type):
    return "%s::%s" % (fieldname, type)


anysql.register_uri_backend('postgresql', connect_by_uri, psycopg2, None, escape, cast)
