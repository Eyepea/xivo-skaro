#!/usr/bin/env python
import unittest
import sys
import os
import shutil
import filecmp
import time

sys.path.append(".") 
from xivo_ha.manage_cluster import ClusterResourceManager
from xivo_ha.manage_cluster import DatabaseManagement

class ClusterResourceManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir     = "tests/tmp"
        self.backup_dir   = "%s/var/backups/pf-xivo/pf-xivo-ha" % self.test_dir
        self.etc_dir      = "%s/etc/pf-xivo/xivo_ha/" % self.test_dir

        #self.services     = ['asterisk', 'dhcpd', 'monit', 'mailto', 'lighttpd'] 
        self.services     = ['asterisk', 'lighttpd'] 
        self.cluster_cfg  = "%s/cluster.cfg" % self.etc_dir
        self.backup_file  = "pf-xivo-ha.bck"
        self.cluster_name = "xivo"
        self.cluster_addr = "192.168.1.34"
        self.cluster_itf  = "eth0"
        self.cluster_group = True

        self.data                = ClusterResourceManager(
                                        services         = self.services, 
                                        backup_directory = self.backup_dir,
                                        cluster_name     = self.cluster_name,
                                        cluster_group    = self.cluster_group,
                                        cluster_addr     = self.cluster_addr,
                                        cluster_itf      = self.cluster_itf,
                                        cluster_cfg      = self.cluster_cfg,
                                   )
        for dir_ in (self.backup_dir, self.etc_dir):
            if os.path.isdir(dir_):
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

    def test_cluster_check_if_configurable(self):
        expect = 'NO resources configured'
        data = self.data._cluster_check_if_configurable()
        self.assertTrue(data)

    def test_cluster_property(self):
        expected = ["property stonith-enabled=false", "property no-quorum-policy=ignore"]
        data = self.data._cluster_property()
        self.assertEqual(data, expected)

    def test_cluster_rsc_defaults(self):
        expected = ['rsc_defaults resource-stickiness=100']
        data = self.data._cluster_rsc_defaults('resource-stickiness=100')
        self.assertEqual(data, expected)

    def test_resource_primitive(self):
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

    
    def test_resources_order_group(self):
        expected = 'order order_xivo inf: ip_xivo:start group_xivo:start'
        data = self.data._resources_order()
        self.assertEqual(expected, data)

    def test_resources_order_services(self):
        self.data.cluster_group = False
        expected = 'order order_xivo inf: ip_xivo:start asterisk:start lighttpd:start'
        data = self.data._resources_order()
        self.assertEqual(expected, data)

    def test_resources_colocation_group(self):
        expected = 'colocation colocation_xivo inf: ip_xivo group_xivo'
        data = self.data._resources_colocation()
        self.assertEqual(expected, data)

    def test_resources_colocation_services(self):
        self.data.cluster_group = False
        expected = 'colocation colocation_xivo inf: ip_xivo asterisk lighttpd'
        data = self.data._resources_colocation()
        self.assertEqual(expected, data)


    def test_resource_group(self):
        expected = 'group group_xivo disk0 fs0 internal_ip apache meta target_role=stopped'
        data = self.data._resource_group(group_meta = 'target_role=stopped',
                                         group_name = 'xivo', 
                                         resources = ['disk0', 'fs0', 'internal_ip', 'apache'])
        self.assertEqual(expected, data)

    def test_resource_monitor(self):
        expected = 'monitor apcfence 60m:60s'
        data = self.data._resource_monitor('apcfence',
                                           monitor_interval = '60',
                                           monitor_timeout  = '60')
        self.assertEqual(expected, data)

    #def test_resource_master_slave(self):
    #    pass

    #def test_cluster_configure_service(self):
    #    pass

    def test_cluster_addr(self):
        expected = 'primitive ip_xivo ocf:heartbeat:IPaddr2 params ip="192.168.1.34" nic="eth0"'
        data = self.data._cluster_addr()
        self.assertEqual(expected, data)

    def test_cluster_create_config_file(self):
        config_file = self.data._cluster_configure()
        self.assertTrue(os.path.isfile(config_file))
        os.rename(config_file, "/tmp/cluster.cfg")

    def test_cluster_push_config(self):
        config_file = self.data._cluster_configure()
        data = self.data._cluster_push_config()
        self.assertTrue(data)

    def test_cluster_backup(self) :
        for f in os.listdir(self.backup_dir):
            # do not delete self.backup_file
            if f != self.backup_file:
                os.remove("%s/%s" % (self.backup_dir, f))
        self.assertTrue(self.data._cluster_backup(self.backup_dir))
    
    def test_cluster_backup_with_backup_file(self) :
        self.filepath = "%s/%s" % (self.backup_dir, self.backup_file)
        if os.path.isfile(self.filepath):
            os.rename(self.filepath, "%s.old" % self.filepath)
        self.data._cluster_backup(filename = self.backup_file)
        self.assertTrue(os.path.isfile(self.filepath))

    def test_cluster_restore_without_filename(self) :
        self.assertRaises(IOError, self.data._cluster_restore)
    
    def _reset_cluster(self):
        self.data._cluster_stop_all_resources()
        self._erase_cluster_configuration()
        config_file = self.data._cluster_configure()
        data = self.data._cluster_push_config()
        time.sleep(1)

    def test_cluster_restore_with_backup_file(self) :
        self._reset_cluster()
        self.data._cluster_backup(filename = self.backup_file)
        self.data._cluster_stop_all_resources()
        self._erase_cluster_configuration()
        self.assertTrue(self.data._cluster_restore(filename = self.backup_file))

    def test_cluster_resource_state(self):
        self._reset_cluster()
        data_ast   = self.data._cluster_resource_state("asterisk")
        self.assertEqual('running', data_ast)

    def test_get_all_resources(self):
        expected = ['ip_xivo', 'asterisk', 'lighttpd']
        data     = self.data._cluster_get_all_resources()
        self.assertEqual(expected, data)

    def test_zzzcluster_stop_all_resources(self):
        self.assertTrue(self.data._cluster_stop_all_resources())
        self._erase_cluster_configuration()

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

