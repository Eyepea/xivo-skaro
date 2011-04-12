#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
sys.path.append("..") 
from xivo_ha.manage_cluster import ClusterResourceManager
from xivo_ha.manage_cluster import DatabaseManagement

class ClusterResourceManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.data           = ClusterResourceManager()
        self.backup_dir = "tmp/backup"
        if not os.path.isdir(self.backup_dir):
            os.makedirs(self.backup_dir)

    def test_update_not_implemented(self):
        self.assertRaises(NotImplementedError, self.data.update)

    def test_cluster_command_without_args(self):
        self.assertRaises(ValueError, self.data._cluster_command)

    def test_cluster_command_with_bad_args(self):
        data = ClusterResourceManager()
        args = ["rkvtr", "configure", "show"]
        self.assertRaises(OSError, data._cluster_command, args)

    def test_cluster_command(self):
        data = ClusterResourceManager()
        args = ["crm", "configure", "show"]
        self.assertTrue(data._cluster_command(args))

    def test_backup_old_configuration(self) :
        for f in os.listdir(self.backup_dir):
            os.remove("%s/%s" % (self.backup_dir, f))
        file_ = self.data._backup_old_configuration(self.backup_dir)
        self.assertTrue(file_)
    
    def test_configure_global_option(self):
        self.data._cluster_global_option()


class DatabaseManagementTestCase(unittest.TestCase):
    def test_update_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.initialize)

    def test_initialize_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.initialize)

if __name__ == '__main__':
    unittest.main()

