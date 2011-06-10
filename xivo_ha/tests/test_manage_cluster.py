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
        self.backup_dir   = "%s/var/backups/pf-xivo/xivo_ha" % self.test_dir
        self.etc_dir      = "%s/etc/pf-xivo/xivo_ha/" % self.test_dir

                               #'scripts': ['/root/pf-xivo-ha/tests/templates/script-1.sh', '/root/pf-xivo-ha/tests/templates/script-2.sh'],
        self.cluster_cfg  = "%s/cluster.cfg" % self.etc_dir
        self.backup_file  = "pf-xivo-ha.bck"
        self.cluster_data = {'cluster_name': 'xivo',
                              'cluster_nodes': ['ha-xivo-1', 'ha-xivo-2'],
                              'cluster_addr': ['eth0:192.168.1.34', 'eth1:192.168.2.34'],
                              'cluster_monitor': '10s',
                              'cluster_timeout': '60s',
                              'cluster_group': 'yes',
                              'cluster_mailto': 'nhicher@proformatique.com',
                              'cluster_pingd': '192.168.1.254',
                              'services': {'asterisk': {'rsc_class': 'lsb', 'monitor': '30', 'timeout': '15'},
                                           'nginx':    {'rsc_class': 'ocf'},
                                           'csync2':   {'rsc_class': 'ocf', 'monitor': '120', 'timeout': '0'}
                              }
                            }
        self.data                = ClusterResourceManager(
                                        self.cluster_data,
                                        backup_directory = self.backup_dir,
                                        cluster_cfg      = self.cluster_cfg,
                                   )
        for dir_ in (self.backup_dir, self.etc_dir):
            if os.path.isdir(dir_):
                shutil.rmtree(dir_)
            os.makedirs(dir_)

    def _reset_cluster(self):
        self.data._cluster_stop_all_resources()
        self._erase_cluster_configuration()
        self.data._cluster_configure()
        data = self.data._cluster_push_config()

    def _erase_cluster_configuration(self):
        self.data._cluster_erase_configuration()

    def test_cluster_command_without_args(self):
        self.assertRaises(ValueError, self.data._cluster_command)

    def test_cluster_command_with_bad_args(self):
        data = ClusterResourceManager()
        args = ["rkvtr", "configure", "show"]
        self.assertRaises(OSError, data._cluster_command, args)

    def test_cluster_command(self):
        data = ClusterResourceManager(self.cluster_data)
        args = ["crm", "configure", "show"]
        self.assertTrue(data._cluster_command(args))

    def test_cluster_check_if_configurable(self):
        expect = 'NO resources configured'
        data = self.data._cluster_check_if_configurable()
        self.assertTrue(data)

    def test_lsb_status(self):
        os.system("/etc/init.d/ntp start > /dev/null 2>&1")
        # false service
        self.assertFalse(self.data._lsb_status("false_service", "started"))
        # started
        self.assertEqual(self.data._lsb_status("ntp", "started"), "started")
        # stopped
        os.system("/etc/init.d/ntp stop > /dev/null 2>&1")
        self.assertEqual(self.data._lsb_status("ntp", "stopped"), "stopped")


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

    def test_resource_pf_scripts(self):
        expected = 'primitive scripts_xivo ocf:heartbeat:pf-xivo-ha-scripts'
        name, data = self.data._resource_pf_scripts()
        self.assertEqual(data, expected)

    def test_configure_services(self):
        expected = [ 'primitive asterisk lsb:asterisk',
                     'primitive csync2 ocf:heartbeat:csync2',
                     'primitive nginx ocf:heartbeat:nginx'
                   ]
        result = []
        for service, data in self.cluster_data['services'].iteritems():
            result.append(self.data._resource_primitive(service))
        self.assertEqual(sorted(expected), sorted(result))

    def test_resources_location(self):
        # location <id> <rsc> <score>: <node>
        expected = 'location location_xivo group_ip_xivo 100: ha-xivo-1'
        data = self.data._resources_location()
        self.assertEqual(data, expected)
    
    def test_resources_order_group(self):
        expected = 'order order_xivo inf: group_ip_xivo:start group_srv_xivo:start'
        data = self.data._resources_order()
        self.assertEqual(expected, data)

    def test_resources_order_services(self):
        self.data.cluster_group = False
        expected = 'order order_xivo inf: group_ip_xivo:start asterisk:start csync2:start nginx:start'
        data = self.data._resources_order()
        self.assertEqual(expected, data)

    def test_resources_colocation_group(self):
        expected = 'colocation colocation_xivo inf: group_ip_xivo group_srv_xivo'
        data = self.data._resources_colocation()
        self.assertEqual(expected, data)

    def test_resources_colocation_services(self):
        self.data.cluster_group = False
        expected = 'colocation colocation_xivo inf: group_ip_xivo asterisk csync2 nginx'
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
                                           monitor_interval = '60m',
                                           monitor_timeout  = '60s')
        self.assertEqual(expected, data)

    def test_resource_default_monitor(self):
        expected = 'monitor nginx 10s:60s'
        data = self.data._resource_monitor('nginx')
        self.assertEqual(expected, data)

    def test_cluster_configure(self):
        expected = "tests/templates/cluster.cfg"
        result   = self.data._cluster_configure()
        self.assertTrue(filecmp.cmp(expected, result))
        
    def test_resource_master_slave(self):
        pass

    def test_simple_addr(self):
        expected = {'ip_xivo_eth0':   'primitive ip_xivo_eth0 ocf:heartbeat:IPaddr2 params ip="192.168.1.34" nic="eth0" op monitor interval="30s"'}
        data = self.data._cluster_addr(['eth0:192.168.1.34'])
        self.assertEqual(expected, data)

    def test_cluster_addr(self):
        expected = {'ip_xivo_eth0': 
                        'primitive ip_xivo_eth0 ocf:heartbeat:IPaddr2 params ip="192.168.1.34" nic="eth0" op monitor interval="30s"',
                    'ip_xivo_eth1': 
                        'primitive ip_xivo_eth1 ocf:heartbeat:IPaddr2 params ip="192.168.2.34" nic="eth1" op monitor interval="30s"'}
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
    
    def test_cluster_restore_with_backup_file(self) :
        self.data._cluster_backup(filename = self.backup_file)
        self._reset_cluster()
        state = self.data._cluster_restore(filename = self.backup_file)
        self.assertTrue(state)

    def test_get_group_members(self):
        self._reset_cluster()
        ip = sorted(['ip_xivo_eth0', 'ip_xivo_eth1'])
        srv = sorted(['nginx', 'asterisk', 'mailto_xivo', 'csync2', 'scripts_xivo'])
        expected = {'group_ip_xivo': ip,
                    'group_srv_xivo': srv
                   }
        result = self.data._cluster_get_group_members()
        self.assertEqual(expected, result)

    def test_cluster_mailto(self):
        expected = 'primitive mailto_xivo ocf:heartbeat:MailTo params email=%s' % self.cluster_data['cluster_mailto']
        name, result = self.data._cluster_mailto()
        self.assertEqual(expected, result)

    def test_cluster_pingd(self):
        expected = ['primitive pingd_xivo ocf:pacemaker:pingd params host_list=192.168.1.254 multiplier=100',
                    'clone pingdclone pingd_xivo meta globally-unique=false']
        result = self.data._cluster_pingd()
        self.assertEqual(expected, result)

    def test_get_all_resources(self):
        expected = ['ip_xivo', 'asterisk', 'nginx'].sort()
        data     = self.data._cluster_get_all_resources().sort()
        self.assertEqual(expected, data)

    def test_cluster_stop_all_resources(self):
        self._reset_cluster()
        state = self.data._cluster_stop_all_resources()
        self.assertTrue(state)

    def test_manage(self):
        self.assertTrue(self.data.manage())

    #def test_status(self):
    #    self.assertTrue(self.data.status())


class DatabaseManagementTestCase(unittest.TestCase):
    def test_update_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.update)

    def test_initialize_not_implemented(self):
        data = DatabaseManagement()
        self.assertRaises(NotImplementedError, data.initialize)


if __name__ == '__main__':
    os.system("rm -rf tests/tmp")
    unittest.main()

