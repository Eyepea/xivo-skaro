#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Avencall

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

class TestXivo(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	def test_01_uuid(self):
		#NOTE: we suppose test is executed locally
		with open('/usr/share/pf-xivo/XIVO-UUID') as f:
			uuid = f.read()[:-1]

		(resp, data) = self.client.request('GET', '/xivo_uuid', {})
		self.assertEqual(resp.status, 200)

		data = cjson.decode(data)
		self.assertTrue('uuid' in data)
		self.assertEqual(data['uuid'], uuid)
 

if __name__ == '__main__':
	unittest.main()
