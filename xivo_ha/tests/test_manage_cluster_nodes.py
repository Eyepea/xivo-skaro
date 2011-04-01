#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
sys.path.append("..") 
from xivo_ha.manage_nodes import ClusterEngine

class ClusterEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.template = "../templates/corosync"
        self.config   = "%s/corosync.conf" % self.template
        self.tmp_dir  = "tmp"

        if os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        os.mkdir(self.tmp_dir) 
        
        # /etc/default/corosync
        self.default_file = "tmp/corosync"
        f = open(self.default_file, 'w')
        with f:
            f.write("START=no")

        # for corosync config_file
        for num in [1, 2, 3]:
            tmp_file = "%s/corosync_%s.conf" % (self.tmp_dir, num)
            shutil.copy2(self.config, tmp_file)

        self.ip_addr = "192.168.1.1"
        self.mc_addr = "226.194.16.1"
        self.temp_config  = "%s/corosync.conf" % self.tmp_dir
        shutil.copy2(self.config, self.temp_config)

    def test_default_corosync(self):
        data = ClusterEngine(self.ip_addr, self.mc_addr, self.template, default_file = self.default_file) 
        self.assertTrue(data._enabled_corosync())

    def test_create_corosync_config_file(self):
        files = []
        for num in [1, 2]:
            result = "%s/corosync_%s.conf" % (self.tmp_dir, num)
            data = ClusterEngine(self.ip_addr, self.mc_addr, self.template, result)
            result = data._create_corosync_config_file()
            # we add only the new file
            files.append(result[0])
        self.assertTrue(filecmp.cmp(files[0], files[1]))

    def test_create_corosync_config_file_false(self):
        d = {   1 : ("192.168.1.0", "226.194.17.1"),
                2 : ("192.168.2.0", "226.195.17.1")}
        files = []
        for num, ip in d.items():
            # we add only the new file
            result = "%s/corosync_%s.conf" % (self.tmp_dir, num)
            data = ClusterEngine(ip[0], ip[1] , self.template, result)
            result = data._create_corosync_config_file()
            files.append(result[0])
        self.assertFalse(filecmp.cmp(files[0], files[1], shallow = False))

    def test_deploy_config_file(self):
        data = ClusterEngine(self.ip_addr, self.mc_addr , self.template, self.temp_config)
        file_1, file_2 = data._create_corosync_config_file()
        self.assertTrue(data._deploy_config_file(file_1, file_2))

    # TODO find a way to test without service
    #def test_initialize(self):
    #    data = ClusterEngine(self.ip_addr, self.mc_addr , self.template, self.temp_config, self.default_file)
    #    data.initialize()


if __name__ == '__main__':
    unittest.main()

