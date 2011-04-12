#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
sys.path.append("..") 
from xivo_ha.manage_nodes import ClusterEngine
from xivo_ha.manage_nodes import ManageService

class ClusterEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.template = "../templates/corosync"
        self.config   = "%s/corosync.conf" % self.template
        self.ip_addr = "192.168.1.0"
        self.mc_addr = "226.194.16.1"

        self.init_path = "tmp/etc/init.d" 
        self.corosync_path = "tmp/etc/corosync"
        self.default_path = "tmp/etc/default"
        for path in (self.init_path, self.corosync_path, self.default_path):
            if not os.path.isdir(path):
                os.makedirs(path)
        
        # /etc/init.d/corosync
        shutil.copy2("templates/corosync", self.init_path)
        self.init_file = "%s/corosync" % self.init_path
        # /etc/default/corosync

        self.default_file = "tmp/etc/default/corosync"
        f = open(self.default_file, 'w')
        with f:
            f.write("START=no")
        self.data = ClusterEngine(self.ip_addr, self.mc_addr, self.template, default_file = self.default_file) 

    def test_default_corosync(self):
        self.assertTrue(self.data._enabled_corosync())

    def test_template_is_available(self):
        self.assertTrue(self.data._template_available(self.default_file))

    #def test_template_is_not_available(self):
    #    not_file = "tmp/test"
    #    data = ClusterEngine(self.ip_addr, self.mc_addr, default_file = not_file) 
    #    self.assertRaises(IOError, data._template_available(), not_file)

    def test_create_corosync_config_file(self):
        files = []
        for num in [1, 2]:
            temp_file = "%s/corosync_%s.conf" % (self.corosync_path, num)
            shutil.copy2(self.config, temp_file)
            data = ClusterEngine(self.ip_addr, self.mc_addr, self.template, temp_file)
            result = data._create_corosync_config_file()
            # we add only the new file
            files.append(result[0])
        self.assertTrue(filecmp.cmp(files[0], files[1]))

    def test_create_corosync_config_file_false(self):
        d = {   3 : ("192.168.1.0", "226.194.17.1"),
                4 : ("192.168.2.0", "226.195.17.1")}
        files = []
        for num, ip in d.items():
            temp_file = "%s/corosync_%s.conf" % (self.corosync_path, num)
            shutil.copy2(self.config, temp_file)
            temp_file = "%s/corosync_%s.conf" % (self.corosync_path, num)
            data = ClusterEngine(ip[0], ip[1] , self.template, temp_file)
            result = data._create_corosync_config_file()
            # we add only the new file
            files.append(result[0])
        self.assertFalse(filecmp.cmp(files[0], files[1]))

    def test_deploy_config_file(self):
        temp_config  = "%s/corosync.conf" % self.corosync_path
        shutil.copy2(self.config, temp_config)
        data = ClusterEngine(self.ip_addr, self.mc_addr , self.template, temp_config)
        file_1, file_2 = data._create_corosync_config_file()
        self.assertTrue(data._deploy_config_file(file_1, file_2))

    def test_initialize(self):
        temp_config  = "%s/corosync.conf" % self.corosync_path
        shutil.copy2(self.config, temp_config)
        data = ClusterEngine(self.ip_addr, self.mc_addr , self.template, temp_config,
                              self.default_file, self.init_file)
        state = data.initialize()
        self.assertTrue(state)

class ManageServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.init_path = "tmp/etc/init.d" 
        shutil.copy2("templates/service", self.init_path)

    def test_is_not_available(self):
        data = ManageService("service-linux", self.init_path)
        self.assertFalse(data._is_available())

    def test_is_not_available(self):
        data = ManageService("service-linux", self.init_path, init_name = 'service')
        self.assertTrue(data._is_available())

if __name__ == '__main__':
    unittest.main()

