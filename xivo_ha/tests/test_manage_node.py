#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
import hashlib

from xivo_ha.tools import Tools
from xivo_ha.manage_nodes import ClusterEngine
from xivo_ha.manage_nodes import ManageService
from xivo_ha.manage_nodes import FilesReplicationManagement

class ClusterEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.template      = "templates/corosync"
        self.config        = "%s/corosync.conf" % self.template
        self.ip_addr       = "192.168.1.0"
        self.mc_addr       = "226.194.16.1"
        self.test_dir      =  "tests/tmp"

        self.init_path = "%s/etc/init.d"  % self.test_dir
        self.corosync_path = "%s/etc/corosync" % self.test_dir
        self.default_path = "%s/etc/default" % self.test_dir
        for path in (self.init_path, self.corosync_path, self.default_path):
            if not os.path.isdir(path):
                os.makedirs(path)
        
        # /etc/init.d/corosync
        shutil.copy2("tests/templates/corosync", self.init_path)
        self.init_file = "%s/corosync" % self.init_path
        # /etc/default/corosync

        self.default_file = "%s/corosync" % self.default_path
        f = open(self.default_file, 'w')
        with f:
            f.write("START=no")
        self.data = ClusterEngine(self.ip_addr, self.mc_addr, self.template, default_file = self.default_file) 

    def test_default_corosync(self):
        self.assertTrue(self.data._enabled_corosync())

    def test_template_is_available(self):
        self.assertTrue(self.data._template_available(self.default_file))

    def test_template_is_not_available(self):
        not_file = "tmp/test"
        data = ClusterEngine(self.ip_addr, self.mc_addr, default_file = not_file) 
        self.assertRaises(IOError, data._template_available, not_file)

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
        self.assertFalse(filecmp.cmp(files[0], files[1], shallow = False))

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
        self.init_path = "tests/tmp/etc/init.d" 
        os.makedirs(self.init_path)
        shutil.copy2("tests/templates/service", self.init_path)

    def test_is_not_available(self):
        data = ManageService("service-linux", self.init_path)
        self.assertFalse(data._is_available())

    def test_is_not_available(self):
        data = ManageService("service-linux", self.init_path, init_name = 'service')
        self.assertTrue(data._is_available())

class FilesReplicationManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir     = "tests/tmp"
        self.etc_dir      = "%s/etc" % self.test_dir
        self.backup_dir   = "%s/var/backups/pf-xivo/xivo_ha" % self.test_dir
        self.csync_data   = {'conflict_resolution': 'younger',
                             'key_file': '%s/csync2.key' % self.etc_dir,
                             'backup_keep': '3',
                             'hosts': ['ha-xivo-1', 'ha-xivo-2'],
                             'config_file': '%s/csync2.cfg' % self.etc_dir,
                             'extra_include': ['/etc/vim', '/etc/python'],
                             'extra_exclude': ['/etc/vim/vimrc'],
                             'role': 'master'
                            }
        self.data         = FilesReplicationManagement(self.csync_data)
        for dir_ in (self.backup_dir, self.etc_dir, self.backup_dir):
            if os.path.isdir(dir_):
                shutil.rmtree(dir_)
            os.makedirs(dir_)

    def test_generate_ssl_key(self):
        string = "%s%s%s" % (self.csync_data['hosts'][0], self.csync_data['hosts'][1], '123456')
        expected = hashlib.md5(string).hexdigest()
        data = self.data._generate_ssl_key(time = 123456)
        self.assertEqual(expected, data)

    def test_create_key_file(self):
        file_ = self.data._create_key_file()
        self.assertTrue(os.path.isfile(file_))

    def test_config_file_hosts_without_itf(self):
        self.csync_data['data_itf'] = None
        expected = "host ha-xivo-1 ha-xivo-2;" 
        result   = self.data._config_file_hosts()
        self.assertEqual(expected, result)

    def test_config_file_hosts_with_itf(self):
        csync_data = self.csync_data
        itf        = csync_data['data_itf'] = 'eth0.10'
        self.data  = FilesReplicationManagement(csync_data)
        expected   = "host ha-xivo-1@ha-xivo-1-%s ha-xivo-2@ha-xivo-2-%s;" % (itf, itf)
        result     = self.data._config_file_hosts()
        self.assertEqual(expected, result)

    def test_config_file_key_file(self):
        expected = "key %s;" % self.data.key_file 
        result   = self.data._config_file_key()
        self.assertEqual(expected, result)

    def test_config_file_backup_dir(self):
        expected = "backup-directory %s;" % self.data.backup_dir
        result   = self.data._config_file_backup_dir()
        self.assertEqual(expected, result)

    def test_config_file_backup_rotate(self):
        expected = "backup-generations %s;" % self.data.backup_keep
        result   = self.data._config_file_backup_rotate()
        self.assertEqual(expected, result)

    def test_config_file_conflict_resolution(self):
        expected = "auto %s;" % self.data.conflict_res
        result   = self.data._config_file_conflict_resolution()
        self.assertEqual(expected, result)

    def test_clean_files_for_sync(self):
        self.data._clean_files_for_sync()

    def test_create_config_file(self):
        expected = "tests/templates/csync2.cfg"
        result   = self.data._create_config_file()
        self.assertTrue(filecmp.cmp(expected, result))

    def test_initialize(self):
        self.data.initialize()

if __name__ == '__main__':
    os.system("rm -rf tests/tmp")
    unittest.main()

