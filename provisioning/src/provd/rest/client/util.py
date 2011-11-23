# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Avencall

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

import functools
import urllib2
from weakref import WeakKeyDictionary


def once(fun):
    # Decorator to use on regular function (NOT on method)
    cache = []
    @functools.wraps(fun)
    def aux(*args, **kwargs):
        try:
            return cache[0]
        except IndexError:
            cache.append(fun(*args, **kwargs))
            return cache[0]
    return aux


def once_per_instance(fun):
    # Decorator to use on method (NOT on regular function)
    cache_dict = WeakKeyDictionary()
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        try:
            return cache_dict[self]
        except KeyError:
            cache_dict[self] = fun(self, *args, **kwargs)
            return cache_dict[self]
    return aux


class DeleteRequest(urllib2.Request):
    def get_method(self):
        return "DELETE"


class PutRequest(urllib2.Request):
    def get_method(self):
        return "PUT"
