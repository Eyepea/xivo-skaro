# -*- coding: UTF-8 -*-

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

import logging
from itertools import ifilter, imap
from provd.persist.common import ID_KEY, InvalidIdError
from twisted.internet import defer
from zope.interface import Interface

logger = logging.getLogger(__name__)


def _retrieve_doc_values(s_key, doc):
    # Return an iterator of matched value, i.e. all the value in the
    # doc that matches the select key
    def aux(current_s_key, current_doc):
        pre, sep, post = current_s_key.partition(u'.')
        if not sep:
            assert pre == current_s_key
            if isinstance(current_doc, dict):
                if current_s_key in current_doc:
                    yield current_doc[current_s_key]
            elif isinstance(current_doc, list):
                for elem in current_doc:
                    for result in aux(current_s_key, elem): 
                        yield result
        else:
            assert pre != current_s_key
            if post is None:
                raise ValueError('invalid selector key "%s"' % s_key)
            
            if isinstance(current_doc, dict) and pre in current_doc:
                for result in aux(post, current_doc[pre]):
                    yield result
    return aux(s_key, doc)


def _contains_operator(selector_value):
    # Return true if the value associated with a key of a selector
    # is an operator value, i.e. has an operator semantic.
    if isinstance(selector_value, dict):
        for k in selector_value.iterkeys():
            if k.startswith(u'$'):
                return True
    return False


def _new_simple_matcher_from_pred(pred):
    # Return a matcher that returns true if there's a value in the document
    # matching the select key for which pred(value) is true
    def aux(s_key, doc):
        for doc_value in _retrieve_doc_values(s_key, doc):
            if pred(doc_value):
                return True
        return False
    return aux


def _new_simple_inv_matcher_from_pred(pred):
    # Return a matcher that returns true if there's no value in the document
    # matching the select key for which pred(value) is true
    def aux(s_key, doc):
        for doc_value in _retrieve_doc_values(s_key, doc):
            if pred(doc_value):
                return False
        return True
    return aux


def _new_in_matcher(s_value):
    # Return a matcher that returns true if there's a value in the document
    # matching the select key that is equal to one of the value in s_value
    if not isinstance(s_value, list):
        raise ValueError('selector value for in matcher must be a list: %s is not' % s_value)
    pred = lambda doc_value: doc_value in s_value
    return _new_simple_matcher_from_pred(pred)


def _new_contains_matcher(s_value):
    # Return a matcher that returns true if there's a value in the document
    # matching the select key that one of the value in s_value
    pred = lambda doc_value: hasattr(doc_value, '__contains__') and s_value in doc_value
    return _new_simple_matcher_from_pred(pred)


def _new_nin_matcher(s_value):
    # Return a matcher that returns true if there's no values in the document
    # matching the select key that is equal to one of the value in s_value
    if not isinstance(s_value, list):
        raise ValueError('selector value for nin matcher must be a list: %s is not' % s_value)
    pred = lambda doc_value: doc_value in s_value
    return _new_simple_inv_matcher_from_pred(pred)


def _new_eq_matcher(s_value):
    # Return a matcher that returns true if there's a value in the document
    # matching the select key that is equal to s_value
    pred = lambda doc_value: doc_value == s_value
    return _new_simple_matcher_from_pred(pred)


def _new_ne_matcher(s_value):
    # Return a matcher that returns true if there's no value in the document
    # matching the select key that is equal to s_value
    pred = lambda doc_value: doc_value == s_value
    return _new_simple_inv_matcher_from_pred(pred)


def _new_gt_matcher(s_value):
    # Return a matcher that returns true if there's a value in the document
    # matching the select key that is greater (>) to s_value
    pred = lambda doc_value: doc_value > s_value
    return _new_simple_matcher_from_pred(pred)


def _new_ge_matcher(s_value):
    pred = lambda doc_value: doc_value >= s_value
    return _new_simple_matcher_from_pred(pred)


def _new_lt_matcher(s_value):
    pred = lambda doc_value: doc_value < s_value
    return _new_simple_matcher_from_pred(pred)


def _new_le_matcher(s_value):
    pred = lambda doc_value: doc_value <= s_value
    return _new_simple_matcher_from_pred(pred)


def _new_exists_matcher(s_value):
    s_value = bool(s_value)
    def aux(s_key, doc):
        it = iter(_retrieve_doc_values(s_key, doc))
        try:
            it.next()
        except StopIteration:
            return not s_value
        else:
            return s_value
    return aux


def _new_and_matcher(matchers):
    # Return true if all the given matchers returns true.
    def aux(s_key, doc):
        for matcher in matchers:
            if not matcher(s_key, doc):
                return False
        return True
    return aux


_MATCHER_FACTORIES = {
    u'$in': _new_in_matcher,
    u'$nin': _new_nin_matcher,
    u'$contains': _new_contains_matcher,
    u'$gt': _new_gt_matcher,
    u'$ge': _new_ge_matcher,
    u'$lt': _new_lt_matcher,
    u'$le': _new_le_matcher,
    u'$ne': _new_ne_matcher,
    u'$exists': _new_exists_matcher,
}

def _new_operator_matcher(operator_key, operator_value):
    try:
        matcher_factory = _MATCHER_FACTORIES[operator_key]
    except KeyError:
        raise ValueError('invalid operator: %s' % operator_key)
    else:
        return matcher_factory(operator_value)


def _new_matcher(s_value):
    # Return a predicate taking a select key and a document that returns true
    # if the document value matches it, else false.
    if _contains_operator(s_value):
        matchers = [_new_operator_matcher(k, v) for k, v in s_value.iteritems()]
        if len(matchers) == 1:
            matcher = matchers[0]
        else:
            matcher = _new_and_matcher(matchers)
        return matcher
    else:
        return _new_eq_matcher(s_value)


def _create_pred_from_selector(selector):
    # Return a predicate taking a document as argument and returning
    # true if the selector matches it, else false.
    selector_matchers = [(k, _new_matcher(v)) for k, v in selector.iteritems()]
    def aux(document):
        for s_key, matcher in selector_matchers:
            if not matcher(s_key, document):
                return False
        return True
    return aux


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
        self._indexes = {}
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
        self._add_document_update_indexes(document)
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
            old_document = self._backend[id]
            self._backend[id] = document
            self._update_document_update_indexes(document, old_document)
            return defer.succeed(None)
    
    def delete(self, id):
        try:
            old_document = self._backend[id]
            self._del_document_update_indexes(old_document)
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
    
    def _new_key_fun_from_key(self, key):
        # Return a function usable for the key parameter of the sorted function
        # from a [sort] key
        splitted_key = key.split(u'.')
        def aux(document):
            cur_elem = document
            try:
                for cur_key in splitted_key:
                    cur_elem = cur_elem[cur_key]
            except (KeyError, TypeError):
                # document does not have the given key -- return None
                return None
            else:
                return cur_elem
        return aux
    
    def _reverse_from_direction(self, direction):
        # Return the reverse value for the reverse parameter of the sorted
        # function from a [sort] direction
        if direction == 1:
            return False
        elif direction == -1:
            return True
        else:
            # XXX should probably create a more meaningful exception class
            raise Exception('invalid direction %s' % direction)
    
    def _do_find_sorted(self, selector, fields, skip, limit, sort):
        documents = list(self._do_find_unsorted(selector, fields, 0, 0))
        key, direction = sort
        key_fun = self._new_key_fun_from_key(key)
        reverse = self._reverse_from_direction(direction)
        documents.sort(key=key_fun, reverse=reverse)
        documents = self._new_skip_iterator(skip, documents)
        documents = self._new_limit_iterator(limit, documents)
        return documents
    
    def _new_fields_map_function(self, fields):
        if not fields:
            return lambda x: x
        else:
            splitted_keys = [field.split(u'.') for field in fields]
            def aux(document):
                result = {ID_KEY: document[ID_KEY]}
                for splitted_key in splitted_keys:
                    cur_elem = document
                    try:
                        for cur_key in splitted_key:
                            cur_elem = cur_elem[cur_key]
                    except (KeyError, TypeError):
                        # element does not have the given key or is not a dictionary -- ignore
                        pass
                    else:
                        cur_result = result
                        for cur_key in splitted_key[:-1]:
                            cur_result = cur_result.setdefault(cur_key, {})
                        cur_result[splitted_key[-1]] = cur_elem
                return result
            return aux
    
    def _new_skip_iterator(self, skip, documents):
        try:
            documents = iter(documents)
            while skip > 0:
                skip -= 1
                documents.next()
        except StopIteration:
            # skip is larger than the number of elements -- do nothing
            pass
        return documents
    
    def _new_limit_iterator(self, limit, documents):
        if not limit:
            return documents
        else:
            def aux(limit):
                # limit is an argument to aux, else it will raise an
                # UnboundLocalVariable exception (since we are using python 2)
                try:
                    while limit > 0:
                        limit -= 1
                        yield documents.next()
                except StopIteration:
                    # limit is larger than the number of elements -- do nothing
                    pass
            return aux(limit)
    
    def _new_iterator(self, selector, documents):
        # Return an iterator that will return every documents matching
        # the given "regular" selector
        pred = _create_pred_from_selector(selector)
        return ifilter(pred, documents)
    
    def _new_indexes_iterator(self, indexes_selector):
        # Return an iterator that will return every documents in the backend
        # matching the given "indexes" selector. Note that an indexes selector
        # can't be empty.
        ids = set()
        first_loop = True
        for selector_key, selector_value in indexes_selector.iteritems():
            index = self._indexes[selector_key]
            index_entry = index.get(selector_value, [])
            if first_loop:
                first_loop = False
                ids.update(index_entry)
            else:
                ids.intersection_update(index_entry)
        for id in ids:
            yield self._backend[id]
    
    def _new_iterator_over_matching_documents(self, selector):
        # Return an iterator that will yield every document in the backend
        # matching the given selector. This may or may not use indices.
        # 1. check if there's some key-value in the selector usable by the
        #    indexes
        indexes_selector = {}
        regular_selector = {}
        for selector_key, selector_value in selector.iteritems():
            if (selector_key in self._indexes and 
                not _contains_operator(selector_value)):
                indexes_selector[selector_key] = selector_value
            else:
                regular_selector[selector_key] = selector_value
        # 2. use indexes selector if possible
        if indexes_selector:
            documents = self._new_indexes_iterator(indexes_selector)
        else:
            documents = self._backend.itervalues()
        # 3. use regular selector if possible
        if regular_selector:
            documents = self._new_iterator(regular_selector, documents)
        return documents
    
    def _do_find_unsorted(self, selector, fields, skip, limit):
        documents = self._new_iterator_over_matching_documents(selector)
        documents = self._new_skip_iterator(skip, documents)
        documents = self._new_limit_iterator(limit, documents)
        documents = imap(self._new_fields_map_function(fields), documents)
        return documents
    
    def _do_find(self, selector, fields, skip, limit, sort):
        # Return an iterator over the documents
        if sort:
            return self._do_find_sorted(selector, fields, skip, limit, sort)
        else:
            return self._do_find_unsorted(selector, fields, skip, limit)
    
    def find(self, selector, fields=None, skip=0, limit=0, sort=None):
        logger.debug('Executing find in backend based collection with:\n'
                     '  selector: %s\n'
                     '  fields: %s\n'
                     '  skip: %s\n'
                     '  limit: %s\n'
                     '  sort: %s',
                     selector, fields, skip, limit, sort)
        return defer.succeed(self._do_find(selector, fields, skip, limit, sort))
    
    def find_one(self, selector):
        it = self._do_find(selector, None, 0, 1, None)
        try:
            result = it.next()
        except StopIteration:
            result = None
        return defer.succeed(result)
    
    def _add_document_update_indexes(self, document):
        # Update the indexes after adding a document to the backend.
        id = document[ID_KEY]
        for complex_key, index in self._indexes.iteritems():
            has_key, value = self._get_value_from_complex_key(complex_key, document)
            if has_key:
                self._new_value_for_index(index, id, value)
    
    def _update_document_update_indexes(self, document, old_document):
        # Update the indexes after updating a document to the backend.
        self._del_document_update_indexes(old_document)
        self._add_document_update_indexes(document)
    
    def _del_document_update_indexes(self, old_document):
        # Update the indexes after removing document from the backend.
        id = old_document[ID_KEY]
        for complex_key, index in self._indexes.iteritems():
            has_key, value = self._get_value_from_complex_key(complex_key, old_document)
            if has_key:
                self._del_value_for_index(index, id, value)
    
    def _new_value_for_index(self, index, id, value):
        # Add the value belonging to the document with the given id to the
        # given index.
        def aux(value):
            if value in index:
                index_entry = index[value]
                if id not in index_entry:
                    index_entry.append(id)
            else:
                index[value] = [id]
        aux(value)
        if isinstance(value, list):
            for list_item in value:
                aux(list_item)
    
    def _del_value_for_index(self, index, id, value):
        # Delete the value belonging to the document with the given id to
        # the given index.
        def aux(value):
            index_entry = index[value]
            index_entry.remove(id)
            if not index_entry:
                del index[value]
        aux(value)
        if isinstance(value, list):
            for list_item in value:
                aux(list_item)
    
    def _get_value_from_complex_key(self, complex_key, document):
        get_value_fun = self._new_get_value_fun_from_complex_key(complex_key)
        return get_value_fun(document)
    
    def _new_get_value_fun_from_complex_key(self, complex_key):
        # Return a function that takes a document and return a tuple where
        # the first element is true if the document has the complex key, and
        # the second element is the value of the complex key for this document
        key_tokens = complex_key.split(u'.')
        def aux(document):
            value = document
            for key_token in key_tokens:
                try:
                    if key_token in value:
                        value = value[key_token]
                    else:
                        break
                except TypeError:
                    break
            else:
                # document has the key and value is the value of this key for
                # this document
                return True, value
            return False, None
        return aux
    
    def _new_id_and_value_iterator(self, complex_key):
        # Return an iterator that yield (id, value) tuple for each document
        # in the backend that has the given complex key.
        get_value_fun = self._new_get_value_fun_from_complex_key(complex_key)
        for document in self._backend.itervalues():
            has_key, value = get_value_fun(document)
            if has_key:
                yield document[ID_KEY], value
    
    def _create_index(self, complex_key):
        logger.debug('Creating index on complex key %s', complex_key)
        index = {}
        for id, value in self._new_id_and_value_iterator(complex_key):
            self._new_value_for_index(index, id, value)
        self._indexes[complex_key] = index
    
    def ensure_index(self, complex_key):
        if complex_key not in self._indexes:
            self._create_index(complex_key)
        return defer.succeed(None)


def new_backend_based_collection(backend, generator):
    return SimpleBackendDocumentCollection(backend, generator)


class ForwardingDocumentCollection(object):
    def __init__(self, collection):
        self._collection = collection
    
    def __getattr__(self, name):
        return getattr(self._collection, name)
