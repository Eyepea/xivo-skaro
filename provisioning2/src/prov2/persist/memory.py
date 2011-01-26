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

import copy
from prov2.persist.common import ID_KEY
from prov2.persist.util import new_backend_based_collection


class DictSimpleBackend(object):
    def __init__(self):
        self._dict = {}
    
    def close(self):
        pass
    
    def __getitem__(self, id):
        return copy.deepcopy(self._dict[id])
    
    def __setitem__(self, id, document):
        self._dict[id] = copy.deepcopy(document)
    
    def __delitem__(self, id):
        del self._dict[id]
    
    def __contains__(self, id):
        return id in self._dict
    
    def itervalues(self):
        for document in self._dict.itervalues():
            yield copy.deepcopy(document)


class ListSimpleBackend(object):
    # Useful for testing when you want to conserve the insertion order...
    def __init__(self):
        self._list = []
    
    def close(self):
        pass
    
    def _find(self, id):
        for i, document in enumerate(self._list):
            if document[ID_KEY] == id:
                return i
        return -1
    
    def __getitem__(self, id):
        idx = self._find(id)
        if idx == -1:
            raise KeyError(id)
        else:
            return copy.deepcopy(self._list[idx])
    
    def __setitem__(self, id, document):
        self._list.append(copy.deepcopy(document))
    
    def __delitem__(self, id):
        idx = self._find(id)
        if idx == -1:
            raise KeyError(id)
        else:
            del self._list[idx]
    
    def __contains__(self, id):
        return self._find(id) != -1
    
    def itervalues(self):
        for document in self._list:
            yield copy.deepcopy(document)


def new_dict_collection(generator):
    return new_backend_based_collection(DictSimpleBackend(), generator)


def new_list_collection(generator):
    return new_backend_based_collection(ListSimpleBackend(), generator)
