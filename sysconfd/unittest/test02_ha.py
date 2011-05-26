#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <g.bour@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""
import unittest, cjson, pprint
import sysconfd_client

class TestHA(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	def test_01_genconf(self):
		conf = {
			'nodes': {
				'network_addr': '192.168.1.0',
				'multicast_addr': '226.194.4.8',
				'first_node': {
					'name': 'ha-xivo-1',
					'ip_addr': '192.168.1.32'
				},
				'second_node': {
					'name': 'ha-xivo-2',
					'ip_addr': '192.168.1.33'
				}
			},

			'cluster': {
				'cluster_name': 'xivo',
				'cluster_addr': [
					'eth0:192.168.1.34',
					'eth0.1:192.168.2.34'
				],
				'cluster_itf_data': 'eth0.1',
				'cluster_group'   : True,
				'cluster_monitor' : 20,
				'cluster_timeout' : 60,
				'cluster_mailto'  : 'gbour@proformatique.com',
				'cluster_pingd'   : '192.168.1.254',

				'services': {
					'asterisk': {
						'rsc_class': 'lsb',
						'monitor'  : 30,
						'timeout'  : 60
					},
					'lighttpd': {
						'rsc_class': 'ocf',
						'monitor'  : 30
					}
				},
			},			
		}

		# push config
		(resp, data) = self.client.request('POST', '/ha_generate', conf)
		self.assertEqual(resp.status, 200)


if __name__ == '__main__':
	unittest.main()
