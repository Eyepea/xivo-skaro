# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2010-2011  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

PROV_MIME_TYPE = 'application/vnd.proformatique.provd+json'


def uri_append_path(base, *path):
    """Append path to base URI.
    
    >>> uri_append_path('http://localhost/', 'foo')
    'http://localhost/foo
    >>> uri_append_path('http://localhost/bar', 'foo')
    'http://localhost/bar/foo'
    >>> uri_append_path('http://localhost/bar', 'foo', 'bar')
    'http://localhost/bar/foo/bar'
    
    """
    if not path:
        return base
    else:
        path_to_append = '/'.join(path)
        if base.endswith('/'):
            fmt = '%s%s'
        else:
            fmt = '%s/%s'
        return fmt % (base, path_to_append)


def uri_append_query(base, query):
    """Append query to base URI.
    
    >>> uri_append_query('http://localhost/', 'id=12')
    'http://localhost/?id=12
    
    """
    return base + '?' + query
