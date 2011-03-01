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

# TODO update to use the non-official async mongo driver, and the new
#      async document collection interface
# TODO add MongoDatabase and MongoDatabaseFactory

from pymongo.errors import DuplicateKeyError
from pymongo.objectid import ObjectId
from provd.persist.common import ID_KEY, InvalidIdError

_MONGO_ID_KEY = u'_id'


def _object_id_generator():
    while True:
        yield unicode(ObjectId())


class MongoDocumentCollection(object):
    def __init__(self, collection, generator=None):
        """
        collection is an instance of pymongo.collection.Collection
        
        """
        self._collection = collection
        self._generator = generator or _object_id_generator()
        self.closed = False
    
    def close(self):
        self.closed = True
    
    if ID_KEY != _MONGO_ID_KEY:
        def _swap_ids(self, document):
            # swap IDs so that if the original document had an '_id' key,
            # not knowing that it has a special meaning for mongodb, we
            # won't lost it's information
            copy = dict(document)
            if ID_KEY in copy:
                del copy[ID_KEY]
            if _MONGO_ID_KEY in copy:
                del copy[_MONGO_ID_KEY]
            if ID_KEY in document:
                copy[_MONGO_ID_KEY] = document[ID_KEY]
            if _MONGO_ID_KEY in document:
                copy[ID_KEY] = document[_MONGO_ID_KEY]
            return copy
    else:
        def _swap_ids(self, document):
            return dict(document)
    
    def _do_insert_with_given_id(self, document_copy):
        assert _MONGO_ID_KEY in document_copy
        try:
            self._collection.insert(document_copy, safe=True)
        except DuplicateKeyError:
            raise InvalidIdError(document_copy[_MONGO_ID_KEY])
    
    def _do_insert_with_generated_id(self, document_copy):
        assert _MONGO_ID_KEY not in document_copy
        while True:
            document_copy[_MONGO_ID_KEY] = self._generator.next()
            try:
                self._collection.insert(document_copy, safe=True)
            except DuplicateKeyError:
                pass
            else:
                break
    
    def insert(self, document):
        document_copy = self._swap_ids(document)
        if _MONGO_ID_KEY in document_copy:
            self._do_insert_with_given_id(document_copy)
        else:
            self._do_insert_with_generated_id(document_copy)
            document[ID_KEY] = document_copy[_MONGO_ID_KEY]
        return document[ID_KEY]
    
    def update(self, document):
        if ID_KEY not in document:
            raise ValueError('no %s key found in document %s' % (ID_KEY, document))
        
        id = document[ID_KEY]
        document_copy = self._swap_ids(document)
        ret = self._collection.update({_MONGO_ID_KEY: id}, document_copy, safe=True)
        if ret[u'n'] == 0:
            raise InvalidIdError(id)
    
    def delete(self, id):
        ret = self._collection.remove(id, safe=True)
        if ret[u'n'] == 0:
            raise InvalidIdError(id)
    
    def retrieve(self, id):
        return self.find_one({_MONGO_ID_KEY: id})
    
    def find_one(self, selector):
        document = self._collection.find_one(selector)
        if document:
            return self._swap_ids(document)
        else:
            return document
    
    def find(self, selector):
        for document in self._collection.find(selector):
            yield self._swap_ids(document)


def new_mongo_collection(mongo_collection, generator=None):
    return MongoDocumentCollection(mongo_collection, generator)
