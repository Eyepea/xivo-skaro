# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

import shelve
from prov2.persist.util import new_backend_based_collection


def _convert_to_backend(self, id):
    # Pre: id is a unicode string
    return id.encode('UTF-8')


class ShelveSimpleBackend(object):
    # in python 2, shelve doesn't accept unicode string as keys, that's why
    # this layer is needed
    
    def __init__(self, filename):
        self._shelve = shelve.open(filename)
    
    def close(self):
        self._shelve.close()
    
    def __getitem__(self, id):
        real_id = _convert_to_backend(id)
        return self._shelve[real_id]
    
    def __setitem__(self, id, document):
        real_id = _convert_to_backend(id)
        self._shelve[real_id] = document
    
    def __delitem__(self, id):
        real_id = _convert_to_backend(id)
        del self._shelve[real_id]
    
    def __contains__(self, id):
        real_id = _convert_to_backend(id)
        return real_id in self._shelve
    
    def itervalues(self):
        return self._shelve.itervalues()


def new_shelve_collection(filename, generator):
    return new_backend_based_collection(ShelveSimpleBackend(filename),
                                        generator)
