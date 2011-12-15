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

import unittest
import provd.persist.memory as memory
from provd.persist.common import ID_KEY
from provd.persist.id import numeric_id_generator, urandom_id_generator
from provd.persist.util import _retrieve_doc_values, _create_pred_from_selector,\
    _create_value_matcher

# TODO fix the test so they all work with the new async interface

def new_dict_collection():
    return memory.new_dict_collection(numeric_id_generator())


def new_list_collection():
    return memory.new_list_collection(numeric_id_generator())


class TestListCollection(unittest.TestCase):
    def setUp(self):
        self._collection = new_list_collection()
    
    def test_preserve_insertion_order(self):
        id_generator = urandom_id_generator()
        documents = [{ID_KEY: id_generator.next()} for i in xrange(500)]
        
        for document in documents:
            self._collection.insert(document)
        for i, document in enumerate(self._collection.find({})):
            self.assertEqual(documents[i], document)

    def test_retrieve_works_correctly(self):
        # XXX invalid test since switch to async
        self._collection.insert({ID_KEY: 'a'})
        self.assertEqual({ID_KEY: 'a'}, self._collection.retrieve('a'))
    
    def test_return_id_on_insert(self):
        id = self._collection.insert({'k': 'v'})
        self.assertNotEqual(None, id)
    
    def test_add_id_to_document_if_absent(self):
        doc = {'k': 'v'}
        self._collection.insert(doc)
        self.assertTrue(ID_KEY in doc)
    
    def test_id_inserted_same_as_returned_on_insert(self):
        # XXX invalid test since switch to async
        doc = {'k': 'v'}
        id = self._collection.insert(doc)
        self.assertTrue(doc[ID_KEY] == id)
    
    def test_leave_id_unchanged_if_present(self):
        id = 'test_id'
        doc = {'k': 'v', ID_KEY: id}
        self._collection.insert(doc)
        self.assertEqual(id, doc[ID_KEY])


class TestDictCollection(unittest.TestCase):
    def setUp(self):
        self._collection = new_dict_collection()
    
    def test_return_id_on_insert(self):
        id = self._collection.insert({'k': 'v'})
        self.assertNotEqual(None, id)
    
    def test_add_id_to_document_if_absent(self):
        doc = {'k': 'v'}
        self._collection.insert(doc)
        self.assertTrue(ID_KEY in doc)
    
    def test_id_inserted_same_as_returned_on_insert(self):
        # XXX invalid test since switch to async
        doc = {'k': 'v'}
        id = self._collection.insert(doc)
        self.assertTrue(doc[ID_KEY] == id)
    
    def test_leave_id_unchanged_if_present(self):
        id = 'test_id'
        doc = {'k': 'v', ID_KEY: id}
        self._collection.insert(doc)
        self.assertEqual(id, doc[ID_KEY])


class TestSelectorSelectValue(unittest.TestCase):
    def test_select_value_simple(self):
        doc = {'k': 'v'}
        self.assertEqual(['v'], list(_retrieve_doc_values('k', doc)))
    
    def test_select_value_simple_with_noise(self):
        doc = {'k': 'v', 'foo': [{'bar': '555'}]}
        self.assertEqual(['v'], list(_retrieve_doc_values('k', doc)))
    
    def test_select_value_simple_no_match(self):
        doc = {}
        self.assertEqual([], list(_retrieve_doc_values('k', doc)))
    
    def test_select_value_dict(self):
        doc = {'k': {'kk': 'v'}}
        self.assertEqual(['v'], list(_retrieve_doc_values('k.kk', doc)))
    
    def test_select_value_dict_3depth(self):
        doc = {'k': {'kk': {'kkk': 'v'}}}
        self.assertEqual(['v'], list(_retrieve_doc_values('k.kk.kkk', doc)))
    
    def test_select_value_list(self):
        doc = {'k': ['v1', 'v2']}
        self.assertEqual(['v1', 'v2'],
                         list(_retrieve_doc_values('k', doc)))
    
    def test_select_value_dict_inside_list(self):
        doc = {'k': [{'kk': 'v'}]}
        self.assertEqual(['v'], list(_retrieve_doc_values('k.kk', doc)))
    
    def test_select_value_dict_inside_list_multiple_values(self):
        doc = {'k': [{'kk': 'v1'}, {'kk': 'v2'}]}
        self.assertEqual(['v1', 'v2'],
                         list(_retrieve_doc_values('k.kk', doc)))


class TestSelectorValueMatcher(unittest.TestCase):
    def test_match_scalar_if_match(self):
        matcher = _create_value_matcher('v')
        self.assertTrue(matcher('v'))
    
    def test_nomatch_scalar_if_no_match(self):
        matcher = _create_value_matcher('v')
        self.assertFalse(matcher('v1'))
    
    def test_match_dict_if_match(self):
        matcher = _create_value_matcher({'k': 'v'})
        self.assertTrue(matcher({'k': 'v'}))
    
    def test_nomatch_dict_if_no_match(self):
        matcher = _create_value_matcher({'k': 'v'})
        self.assertFalse(matcher({'k': 'v1'}))
        self.assertFalse(matcher({'k1': 'v'}))

    def test_match_Sin_if_match(self):
        matcher = _create_value_matcher({'$in': [1, 2]})
        self.assertTrue(matcher(1))
        self.assertTrue(matcher(2))
    
    def test_nomatch_Sin_if_no_match(self):
        matcher = _create_value_matcher({'$in': [1,2]})
        self.assertFalse(matcher(0))
        self.assertFalse(matcher(3))


class TestSelectorCreatePredicate(unittest.TestCase):
    def test_empty_selector_match_anything(self):
        pred = _create_pred_from_selector({})
        self.assertTrue(pred({}))
        self.assertTrue(pred({'k': 'v'}))
        
    def test_simple_1item_selector_match(self):
        pred = _create_pred_from_selector({'k1': 'v1'})
        self.assertTrue(pred({'k1': 'v1'}))
        self.assertTrue(pred({'k1': 'v1', 'k2': 'v2'}))
    
    def test_simple_1item_selector_nomatch(self):
        pred = _create_pred_from_selector({'k1': 'v1'})
        self.assertFalse(pred({}))
        self.assertFalse(pred({'k2': 'v2'}))
        self.assertFalse(pred({'k1': 'v2'}))
    
    def test_simple_2item_selector_match(self):
        pred = _create_pred_from_selector({'k1': 'v1', 'k2': 'v2'})
        self.assertTrue(pred({'k1': 'v1', 'k2': 'v2'}))
        self.assertTrue(pred({'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}))
        
    def test_simple_2item_selector_nomatch(self):
        pred = _create_pred_from_selector({'k1': 'v1', 'k2': 'v2'})
        self.assertFalse(pred({}))
        self.assertFalse(pred({'k1': 'v1'}))
        self.assertFalse(pred({'k2': 'v2'}))
        self.assertFalse(pred({'k1': 'v1', 'k2': 'v1'}))

    def test_1item_list_selector_match(self):
        pred = _create_pred_from_selector({'k1': 'v1'})
        self.assertTrue(pred({'k1': ['v1']}))
        self.assertTrue(pred({'k1': ['v2', 'v1']}))
        self.assertTrue(pred({'k1': 'v1'}))

    def test_1item_list_selector_nomatch(self):
        pred = _create_pred_from_selector({'k1': 'v1'})
        self.assertFalse(pred({'k1': ['v2']}))
        self.assertFalse(pred({'k1': 'v2'}))
    
    def test_1item_dict_selector_match(self):
        pred = _create_pred_from_selector({'k.kk': 'v'})
        self.assertTrue(pred({'k': {'kk': 'v'}}))
        self.assertTrue(pred({'k': {'kk': 'v', 'foo': 'bar'}}))
        self.assertTrue(pred({'k': [{'kk': 'v'}]}))
    
    def test_1item_dict_selector_nomatch(self):
        pred = _create_pred_from_selector({'k.kk': 'v'})
        self.assertFalse(pred({'k': {'kk': 'v1'}}))
        self.assertFalse(pred({'k': 'v'}))
        self.assertFalse(pred({'k': {'foo': 'bar'}}))
        self.assertFalse(pred({'k': [{'kk': 'v1'}]}))
        self.assertFalse(pred({'k': []}))
