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

from provd.persist.common import ID_KEY, InvalidIdError
from twisted.internet import defer
from zope.interface import Interface


def _select_value(select_key, document):
    # Return an iterator of matched value, i.e. all the value in the
    # document that matches the select key
    def aux(current_select_key, current_document):
        pre, sep, post = current_select_key.partition('.')
        if not sep:
            assert pre == current_select_key
            if isinstance(current_document, dict):
                if current_select_key in current_document:
                    value = current_document[current_select_key]
                    if isinstance(value, list):
                        for elem in value:
                            yield elem
                    else:
                        yield value
            elif isinstance(current_document, list):
                for elem in current_document:
                    for result in aux(current_select_key, elem): 
                        yield result
        else:
            assert pre != current_select_key
            if post is None:
                raise ValueError('invalid selector key "%s"' % select_key)
            
            if isinstance(current_document, dict) and pre in current_document:
                for result in aux(post, current_document[pre]):
                    yield result
    return aux(select_key, document)


def _contains_operator(dict_):
    for k in dict_.iterkeys():
        if isinstance(k, basestring) and k.startswith('$'):
            return True
    return False


def _create_value_matcher(select_value):
    """Return a predicate taking a document value as argument and returning
    true if the document value matches it, else false.
    
    """
    # XXX this is quite ugly
    if isinstance(select_value, dict):
        if _contains_operator(select_value):
            if ((len(select_value) != 1 and u'$in' not in select_value) or
                not hasattr(select_value, '__contains__')):
                raise ValueError('invalid selector value "%s"' % select_value)
            else:
                possible_matches = select_value[u'$in']
                def in_matcher(document_value):
                    return document_value in possible_matches
                return in_matcher
    def std_matcher(document_value):
        return select_value == document_value
    return std_matcher


def _create_predicate_from_selector(selector):
    """Return a predicate taking a document as argument and returning
    true if the selector matches it, else false.
    
    """
    def aux(document):
        for select_key, select_value in selector.iteritems():
            matcher = _create_value_matcher(select_value)
            for document_value in _select_value(select_key, document):
                if matcher(document_value):
                    break
            else:
                return False
        return True
    return aux


def find(selector, iterable):
    match = _create_predicate_from_selector(selector)
    for document in iterable:
        if match(document):
            yield document


def find_one(selector, iterable):
    it = find(selector, iterable)
    try:
        return it.next()
    except StopIteration:
        return None


class ISimpleBackend(Interface):
    def close(self):
        pass
    
    def __getitem__(self, id):
        pass
    
    def __setitem__(self, id, document):
        pass
    
    def __delitem__(self, id):
        pass
    
    def __contains__(self, id):
        pass
    
    def itervalues(self):
        pass


class SimpleBackendDocumentCollection(object):
    def __init__(self, backend, generator):
        self._backend = backend
        self._generator = generator
        self.closed = False
    
    def close(self):
        self._backend.close()
        self.closed = True
    
    def _generate_new_id(self):
        while True:
            id = self._generator.next()
            if id not in self._backend:
                return id
    
    def insert(self, document):
        if ID_KEY in document:
            id = document[ID_KEY]
            if id in self._backend:
                raise InvalidIdError(id)
        else:
            id = self._generate_new_id()
            document[ID_KEY] = id
        
        assert id == document[ID_KEY]
        assert id not in self._backend
        self._backend[id] = document
        return defer.succeed(id)
    
    def update(self, document):
        try:
            id = document[ID_KEY]
        except KeyError:
            return defer.fail(ValueError('no %s key found in document %s' %
                                         (ID_KEY, document)))
        else:
            if id not in self._backend:
                return defer.fail(InvalidIdError(id))
            self._backend[id] = document
            return defer.succeed(None)
    
    def delete(self, id):
        try:
            del self._backend[id]
        except KeyError:
            return defer.fail(InvalidIdError(id))
        else:
            return defer.succeed(None)
    
    def retrieve(self, id):
        try:
            return defer.succeed(self._backend[id])
        except KeyError:
            return defer.succeed(None)
    
    def find(self, selector):
        return defer.succeed(find(selector, self._backend.itervalues()))
    
    def find_one(self, selector):
        return defer.succeed(find_one(selector, self._backend.itervalues()))


def new_backend_based_collection(backend, generator):
    return SimpleBackendDocumentCollection(backend, generator)


class ForwardingDocumentCollection(object):
    def __init__(self, collection):
        self.__collection = collection
    
    def close(self):
        self.__collection.close()
    
    def insert(self, document):
        return self.__collection.insert(document)
    
    def update(self, document):
        return self.__collection.update(document)
    
    def delete(self, id):
        return self.__collection.delete(id)
    
    def retrieve(self, id):
        return self.__collection.retrieve(id)
    
    def find(self, selector):
        return self.__collection.find(selector)
    
    def find_one(self, selector):
        return self.__collection.find_one(selector)
