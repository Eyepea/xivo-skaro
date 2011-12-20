# -*- coding: UTF-8 -*-

import unittest
import provd.rest.pycli.pyclient as pyclient


class TestExpandDottedDict(unittest.TestCase):
    def test_empty_dict(self):
        d = {}
        self.assertEqual(d, pyclient._expand_dotted_dict(d))

    def test_non_dotted_dict(self):
        d = {'a': 'v', 'b': 'v'}
        self.assertEqual(d, pyclient._expand_dotted_dict(d))

    def test_one_1_dot_element_dict(self):
        dotted = {'a.b': 'v'}
        expanded = {'a': {'b': 'v'}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_one_2_dots_element_dict(self):
        dotted = {'a.b.c': 'v'}
        expanded = {'a': {'b': {'c': 'v'}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_one_3_dots_element_dict(self):
        dotted = {'a.b.c.d': 'v'}
        expanded = {'a': {'b': {'c': {'d': 'v'}}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_two_elements_mixed_dict(self):
        dotted = {'a.b': 'v', 'aa': 'v'}
        expanded = {'a': {'b': 'v'}, 'aa': 'v'}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_one_1_dot_element_with_2_elements_dict_dict(self):
        dotted = {'a.b': {'c': 'v', 'd': 'v'}}
        expanded = {'a': {'b': {'c': 'v', 'd': 'v'}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_one_1_dot_element_with_dotted_dict_dict(self):
        dotted = {'a.b': {'c.d': 'v'}}
        expanded = {'a': {'b': {'c': {'d': 'v'}}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_one_1_dot_element_with_double_dotted_dict_dict(self):
        dotted = {'a.b': {'c.d': {'e.f': 'v'}}}
        expanded = {'a': {'b': {'c': {'d': {'e': {'f': 'v'}}}}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_two_1_dot_elements_common_dot_dict(self):
        dotted = {'a.b': 'v', 'a.c': 'v'}
        expanded = {'a': {'b': 'v', 'c': 'v'}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_two_2_dots_elements_common_dot_dict(self):
        dotted = {'a.b.c': 'v', 'a.b.d': 'v'}
        expanded = {'a': {'b': {'c': 'v', 'd': 'v'}}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))

    def test_dotted_key_overwrite_dict(self):
        # complex test
        dotted = {'a': 'v1', 'a.b': 'v2'}
        expanded = {'a': {'b': 'v2'}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))
        dotted = {'b': 'v1', 'b.a': 'v2'}
        expanded = {'b': {'a': 'v2'}}
        self.assertEqual(expanded, pyclient._expand_dotted_dict(dotted))
