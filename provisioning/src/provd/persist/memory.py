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

import copy
from provd.persist.common import ID_KEY
from provd.persist.id import get_id_generator_factory
from provd.persist.util import new_backend_based_collection


class DictSimpleBackend(object):
    def __init__(self):
        self._dict = {}
    
    def close(self):
        self._dict = {}
    
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
    # Useful for testing when you want to keep the insertion order...
    def __init__(self):
        self._list = []
    
    def close(self):
        self._list = []
    
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


class MemoryDatabase(object):
    def __init__(self, collection_factory, generator_factory):
        self._collection_factory = collection_factory
        self._generator_factory = generator_factory
        self._collections = {}
    
    def close(self):
        self._collections = {}
    
    def _new_collection(self):
        generator = self._generator_factory()
        return self._collection_factory(generator)
    
    def collection(self, id):
        if id not in self._collections:
            self._collections[id] = self._new_collection()
        return self._collections[id]


class MemoryDatabaseFactory(object):
    def _get_collection_factory(self, type):
        if type == 'list':
            return new_list_collection
        elif type == 'dict':
            return new_dict_collection
        else:
            raise ValueError('unrecognised type "%s"' % type)
    
    def new_database(self, type, generator, **kwargs):
        collection_factory = self._get_collection_factory(type)
        generator_factory = get_id_generator_factory(generator)
        return MemoryDatabase(collection_factory, generator_factory)
