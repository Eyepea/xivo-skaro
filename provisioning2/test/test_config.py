# -*- coding: UTF-8 -*-

import unittest
from prov2.devices.config import ConfigManager, Config, flatten_config,\
    list_config

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.cfg_manager = ConfigManager()
        
    def test_doesnt_lamely_fail(self): 
        cfg1 = Config()
        cfg1[1] = 2
        self.cfg_manager['cfg1'] = cfg1
        
        cfg2 = Config()
        cfg2[2] = 3
        self.cfg_manager['cfg2'] = cfg2
        
        cfg2.fallbacks.add('cfg1')
        self.assertEqual(3, cfg2[2])
        self.assertEqual(2, cfg2[1])


class TestFlattenConfig(unittest.TestCase):
    def test_doesnt_loop_infinitely(self):
        cfg = {}
        cfg_mgr = {'cfg1': (cfg, ['cfg2']),
                   'cfg2': (cfg, ['cfg1']),
                   'cfg3': (cfg, ['cfg3', 'cfg2', 'cfg1'])}
        self.assertEqual({}, flatten_config(cfg_mgr, 'cfg1'))
        self.assertEqual({}, flatten_config(cfg_mgr, 'cfg2'))
        self.assertEqual({}, flatten_config(cfg_mgr, 'cfg3'))
        
    def test_simple_override_correctly(self):
        cfg1 = {'a': 1}
        cfg2 = {'a': 2}
        
        cfg_mgr1 = {'cfg1': (cfg1, []),
                    'cfg2': (cfg2, ['cfg1'])}
        self.assertEqual({'a': 2}, flatten_config(cfg_mgr1, 'cfg2'))
        self.assertEqual({'a': 1}, flatten_config(cfg_mgr1, 'cfg1'))
        
        cfg_mgr2 = {'cfg1': (cfg1, ['cfg2']),
                    'cfg2': (cfg2, [])}
        self.assertEqual({'a': 1}, flatten_config(cfg_mgr2, 'cfg1'))
        self.assertEqual({'a': 2}, flatten_config(cfg_mgr2, 'cfg2'))
    
    def test_simple_inherit_correctly(self):
        cfg1 = {'a': 1}
        cfg2 = {}
        
        cfg_mgr1 = {'cfg1': (cfg1, []), 'cfg2': (cfg2, ['cfg1'])}
        self.assertEqual({'a': 1}, flatten_config(cfg_mgr1, 'cfg2'))
        self.assertEqual({'a': 1}, flatten_config(cfg_mgr1, 'cfg1'))
        
        cfg_mgr2 = {'cfg2': (cfg2, []), 'cfg1': (cfg1, ['cfg2'])}
        self.assertEqual({'a': 1}, flatten_config(cfg_mgr2, 'cfg1'))
        self.assertEqual({}, flatten_config(cfg_mgr2, 'cfg2'))
    
    def test_recursive_inherit_correctly(self):
        cfg1 = {'a': {'a': {1: 1}}}
        cfg2 = {'a': {'a': {2: 2}}}
        
        cfg_mgr1 = {'cfg1': (cfg1, []),
                    'cfg2': (cfg2, ['cfg1'])}
        self.assertEqual({'a': {'a': {1: 1, 2: 2}}}, flatten_config(cfg_mgr1, 'cfg2'))
        
        cfg_mgr2 = {'cfg1': (cfg1, ['cfg2']),
                    'cfg2': (cfg2, [])}
        self.assertEqual({'a': {'a': {1: 1, 2: 2}}}, flatten_config(cfg_mgr2, 'cfg1'))

    def test_list_config_simple(self):
        cfg = {}
        cfg_mgr = {'cfg1': (cfg, []),
                   'cfg2': (cfg, ['cfg1']),
                   'cfg3': (cfg, ['cfg2']),
                   'cfg4': (cfg, ['cfg4']),
                   'cfg5': (cfg, ['cfg4', 'cfg3'])}
        self.assertEqual(set([]), list_config(cfg_mgr, 'cfg1'))
        self.assertEqual(set(['cfg1']), list_config(cfg_mgr, 'cfg2'))
        self.assertEqual(set(['cfg2', 'cfg1']), list_config(cfg_mgr, 'cfg3'))
        self.assertEqual(set([]), list_config(cfg_mgr, 'cfg4'))
        self.assertEqual(set(['cfg4', 'cfg3', 'cfg2', 'cfg1']), list_config(cfg_mgr, 'cfg5'))
