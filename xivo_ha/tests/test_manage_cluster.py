#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
sys.path.append(".") 
from xivo_ha.manage_cluster import ClusterResourceManager
from xivo_ha.manage_cluster import DatabaseManagement

class ClusterResourceManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir            = "tests/tmp"
        self.backup_dir          = "%s/var/backups/pf-xivo/pf-xivo-ha" % self.test_dir
        self.services             = ['asterisk', 'dhcpd', 'monit', 'mailto', 'lighttpd'] 
        self.etc_dir             = "%s/etc/pf-xivo/pf-xivo-ha" % self.test_dir
        self.global_options_file = "%s/global_options" % self.etc_dir
        self.backup_file         = "pf-xivo-ha.bck"
        self.data                = ClusterResourceManager(
                                        services = self.services, 
                                        backup_directory = self.backup_dir,
                                        global_options_file = self.global_options_file,
                                   )
        for dir_ in (self.backup_dir, self.etc_dir):
            shutil.rmtree(dir_)
            os.makedirs(dir_)

    def _erase_cluster_configuration(self):
        self.data._cluster_erase_configuration()

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

    def test_configure_global_option(self):
        ret = self.data._cluster_global_option()[1]
        self.assertEqual(ret, 0)
        
    def test_cluster_backup(self) :
        self.data._cluster_global_option()
        for f in os.listdir(self.backup_dir):
            # do not delete self.backup_file
            if f != self.backup_file:
                os.remove("%s/%s" % (self.backup_dir, f))
        self.assertTrue(self.data._cluster_backup(self.backup_dir))
    
    def test_cluster_backup_with_backup_file(self) :
        self.data._cluster_global_option()
        self.data._cluster_backup(filename = self.backup_file)
        self.filepath = "%s/%s" % (self.backup_dir, self.backup_file)
        self.assertTrue(os.path.isfile(self.filepath))

    def test_cluster_restore(self) :
        self.assertRaises(IOError, self.data._cluster_restore)
    
    def test_cluster_restore_with_backup_file(self) :
        self.data._cluster_global_option()
        self.data._cluster_backup(filename = self.backup_file)
        self._erase_cluster_configuration()
        self.assertTrue(self.data._cluster_restore(filename = self.backup_file))
        
    def test_cluster_check_status(self):
        # without configuration, must return 2
        self._erase_cluster_configuration()
        ret = self.data._cluster_check_status()[1]
        self.assertEqual(ret, 2)
        # configure global
        self.data._cluster_global_option()
        ret = self.data._cluster_check_status()[1]
        self.assertEqual(ret, 0)
       

    def test_resource_primitive(self):
        # _resource_primitive(self, rsc, rsc_class = '', rsc_provider = '', rsc_type = '',
        #                     rsc_params = '', rsc_operation = '', rsc_op = '' ):
        data = self.data._resource_primitive("asterisk", rsc_class = 'lsb')
        self.assertEqual(data, 'primitive asterisk lsb:asterisk')

        #example from http://www.clusterlabs.org/doc/crm_cli.html
        stonith_expect_1 = 'primitive apcfence stonith:apcsmart params ttydev=/dev/ttyS0 hostlist="node1 node2"'
        stonith_expect_2 = ' op start timeout=60s op monitor interval=30m timeout=60s'
        stonith_expected = stonith_expect_1 + stonith_expect_2

        data = self.data._resource_primitive("apcfence", rsc_class = 'stonith',
                                             rsc_provider = 'apcsmart',
                                             rsc_params = 'ttydev=/dev/ttyS0 hostlist="node1 node2"',
                                             rsc_op = ["start timeout=60s", "monitor interval=30m timeout=60s"])
        self.assertEqual(data, stonith_expected)
        data = self.data._resource_primitive("webserver", rsc_class = 'apache',
                                             rsc_params = 'configfile=/etc/apache/www8.conf')
        self.assertEqual(data, 'primitive webserver apache params configfile=/etc/apache/www8.conf')

        mysql_expect_1 = "primitive db0 mysql params config=/etc/mysql/db0.conf"
        mysql_expect_2 = " op monitor interval=60s op monitor interval=300s OCF_CHECK_LEVEL=10"
        mysql_expected = mysql_expect_1 + mysql_expect_2
        data = self.data._resource_primitive("db0", rsc_class = 'mysql',
                                             rsc_params = 'config=/etc/mysql/db0.conf',
                                             rsc_op = ["monitor interval=60s",
                                                       "monitor interval=300s OCF_CHECK_LEVEL=10"])
        self.assertEqual(data, mysql_expected)

        drbd_expect_1 = "primitive r0 ocf:linbit:drbd params drbd_resource=r0"
        drbd_expect_2 = " op monitor role=Master interval=60s op monitor role=Slave interval=300s"
        drbd_expected = drbd_expect_1 + drbd_expect_2
        data = self.data._resource_primitive("r0", rsc_class = 'ocf', rsc_provider = 'linbit',
                                             rsc_type = 'drbd', rsc_params = 'drbd_resource=r0',
                                             rsc_op = ['monitor role=Master interval=60s',
                                                       'monitor role=Slave interval=300s'])
        self.assertEqual(data, drbd_expected)

    def test_resource_order(self):
        pass

    def test_resource_colocation(self):
        pass


    def test_resource_group(self):
        pass

    def test_resource_monitor(self):
        pass

    def test_resource_master_slave(self):
        pass

    def test_cluster_configure_service(self):
        pass

    def test_update_not_implemented(self):
        self.assertRaises(NotImplementedError, self.data.update)


class DatabaseManagementTestCase(unittest.TestCase):
    def test_update_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.initialize)

    def test_initialize_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.initialize)

if __name__ == '__main__':
   unittest.main()

