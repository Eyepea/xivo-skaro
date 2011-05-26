#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

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

class TestDahdi(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	def test_01_infos(self):
		# get infos
		(resp, data) = self.client.request('GET', '/dahdi_get_spansinfo', {})
		print resp.status
		self.assertEqual(resp.status, 200)
		import pprint; pprint.pprint(cjson.decode(data))

		(resp, data) = self.client.request('GET', '/dahdi_get_cardsinfo', {})
		print resp.status
		self.assertEqual(resp.status, 200)
		import pprint; pprint.pprint(cjson.decode(data))

if __name__ == '__main__':
	unittest.main()
