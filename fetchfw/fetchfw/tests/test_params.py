# -*- coding: UTF-8 -*-

import unittest
from fetchfw import params


class TestFilterSection(unittest.TestCase):
    def test_strip_section_name(self):
        config_dict = {'foo.a': 1}
        section_id = 'foo'
        expected = {'a': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_filter_correctly(self):
        config_dict = {'foo.a': 1, 'bar.b': 2}
        section_id = 'foo'
        expected = {'a': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_returns_empty_dict_on_no_match(self):
        config_dict = {'bar.b': 2}
        section_id = 'foo'
        expected = {}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_accept_empty_config_dict(self):
        config_dict = {}
        section_id = 'foo'
        expected = {}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)

    def test_section_id_cant_contain_dot(self):
        self.assertRaises(ValueError, params.filter_section, {}, 'foo.bar')

    def test_option_id_can_contain_dot(self):
        config_dict = {'foo.a.b': 1}
        section_id = 'foo'
        expected = {'a.b': 1}
        self.assertEqual(params.filter_section(config_dict, section_id),
                         expected)


class TestBool(unittest.TestCase):
    def test_true_raw_values(self):
        self.assertTrue(params.bool_('True'))
        self.assertTrue(params.bool_('true'))

    def test_false_raw_values(self):
        self.assertFalse(params.bool_('False'))
        self.assertFalse(params.bool_('false'))

    def test_invalid_raw_values(self):
        self.assertRaises(ValueError, params.bool_, '')
        self.assertRaises(ValueError, params.bool_, 'test')
