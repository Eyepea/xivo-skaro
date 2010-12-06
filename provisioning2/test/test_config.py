# -*- coding: UTF-8 -*-

import unittest
from prov2.devices.config import ConfigManager 


class TestFlattenConfig(unittest.TestCase):
    def test_doesnt_loop_infinitely(self):
        cfg = {}
        cfg_mgr = ConfigManager({
                   'cfg1': (cfg, ['cfg2']),
                   'cfg2': (cfg, ['cfg1']),
                   'cfg3': (cfg, ['cfg3', 'cfg2', 'cfg1'])})
        self.assertEqual({}, cfg_mgr.flatten('cfg1'))
        self.assertEqual({}, cfg_mgr.flatten('cfg2'))
        self.assertEqual({}, cfg_mgr.flatten('cfg3'))
        
    def test_simple_override_correctly(self):
        cfg1 = {'a': 1}
        cfg2 = {'a': 2}
        
        cfg_mgr1 = ConfigManager({
                    'cfg1': (cfg1, []),
                    'cfg2': (cfg2, ['cfg1'])})
        self.assertEqual({'a': 2}, cfg_mgr1.flatten('cfg2'))
        self.assertEqual({'a': 1}, cfg_mgr1.flatten('cfg1'))
        
        cfg_mgr2 = ConfigManager({
                    'cfg1': (cfg1, ['cfg2']),
                    'cfg2': (cfg2, [])})
        self.assertEqual({'a': 1}, cfg_mgr2.flatten('cfg1'))
        self.assertEqual({'a': 2}, cfg_mgr2.flatten('cfg2'))
    
    def test_simple_inherit_correctly(self):
        cfg1 = {'a': 1}
        cfg2 = {}
        
        cfg_mgr1 = ConfigManager({'cfg1': (cfg1, []), 'cfg2': (cfg2, ['cfg1'])})
        self.assertEqual({'a': 1}, cfg_mgr1.flatten('cfg2'))
        self.assertEqual({'a': 1}, cfg_mgr1.flatten('cfg1'))
        
        cfg_mgr2 = ConfigManager({'cfg2': (cfg2, []), 'cfg1': (cfg1, ['cfg2'])})
        self.assertEqual({'a': 1}, cfg_mgr2.flatten('cfg1'))
        self.assertEqual({}, cfg_mgr2.flatten('cfg2'))
    
    def test_recursive_inherit_correctly(self):
        cfg1 = {'a': {'a': {1: 1}}}
        cfg2 = {'a': {'a': {2: 2}}}
        
        cfg_mgr1 = ConfigManager({
                     'cfg1': (cfg1, []),
                     'cfg2': (cfg2, ['cfg1'])})
        self.assertEqual({'a': {'a': {1: 1, 2: 2}}}, cfg_mgr1.flatten('cfg2'))
        
        cfg_mgr2 = ConfigManager({'cfg1': (cfg1, ['cfg2']),
                    'cfg2': (cfg2, [])})
        self.assertEqual({'a': {'a': {1: 1, 2: 2}}}, cfg_mgr2.flatten('cfg1'))

    def test_list_config_simple(self):
        cfg = {}
        cfg_mgr = ConfigManager({
                   'cfg1': (cfg, []),
                   'cfg2': (cfg, ['cfg1']),
                   'cfg3': (cfg, ['cfg2']),
                   'cfg4': (cfg, ['cfg4']),
                   'cfg5': (cfg, ['cfg4', 'cfg3'])})
        self.assertEqual(set([]), cfg_mgr.list('cfg1'))
        self.assertEqual(set(['cfg1']), cfg_mgr.list('cfg2'))
        self.assertEqual(set(['cfg2', 'cfg1']), cfg_mgr.list('cfg3'))
        self.assertEqual(set([]), cfg_mgr.list('cfg4'))
        self.assertEqual(set(['cfg4', 'cfg3', 'cfg2', 'cfg1']), cfg_mgr.list('cfg5'))

    def test_flatten_does_deep_copy(self):
        cfg = {1: {2: {3: 3}}}
        cfg_mgr = ConfigManager({'cfg': (cfg, [])})
        self.assertNotEqual(id(cfg[1][2]), id(cfg_mgr.flatten('cfg')[1][2]))

    def test_required_by_simple(self):
        cfg = {}
        cfg_mgr = ConfigManager({
                    'cfg1': (cfg, []),
                    'cfg2': (cfg, ['cfg1']),
                    'cfg3': (cfg, ['cfg2']),
                    'cfg4': (cfg, ['cfg2']),
                    'cfg5': (cfg, ['cfg2', 'cfg1'])})
        self.assertEqual(set([]), cfg_mgr.required_by('cfg3'))
        self.assertEqual(set([]), cfg_mgr.required_by('cfg4'))
        self.assertEqual(set([]), cfg_mgr.required_by('cfg5'))
        self.assertEqual(set(['cfg3', 'cfg4', 'cfg5']), cfg_mgr.required_by('cfg2'))
        self.assertEqual(set(['cfg2', 'cfg3', 'cfg4', 'cfg5']), cfg_mgr.required_by('cfg1'))
        self.assertEqual(set([]), cfg_mgr.required_by('cfg1', maxdepth=0))
        self.assertEqual(set(['cfg2', 'cfg5']), cfg_mgr.required_by('cfg1', maxdepth=1))

    def test_required_by_should_raise_on_invalid(self):
        cfg_mgr = ConfigManager()
        self.assertRaises(KeyError, cfg_mgr.required_by, 'fa')
