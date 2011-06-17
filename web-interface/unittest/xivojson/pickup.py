# -*- coding: utf-8 -*-
from __future__ import with_statement

__version__ = "$Revision: 8121 $ $Date: 2010-05-14 17:20:24 +0200 (ven. 14 mai 2010) $"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
	Copyright (C) 2010  Proformatique

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
import unittest, pprint, cjson
from xivojson import *
# define global variables
from globals  import *


class Test10Pickup(unittest.TestCase):
	def setUp(self):
		global IP, PORT, SSL, USERNAME, PASSWORD

		self.client = JSONClient(IP, PORT, SSL, USERNAME, PASSWORD)
		self.obj    = 'pickup'

	def test_01_list(self):
		(resp, data) = self.client.list(self.obj)
		self.assertEqual(resp.status, 204) # 204 == empty list
		
	def test_02_add(self):
		with open('xivojson/pickup.json') as f:
			content = cjson.decode(f.read())
		    
		(resp, data) = self.client.add(self.obj, content)
		self.assertEqual(resp.status, 200)


		(resp, data) = self.client.list(self.obj)
		self.assertEqual(resp.status, 200)
		self.assertEqual(len(cjson.decode(data)), 1)

	def test_02_view(self):
		(resp, data) = self.client.view(self.obj, 0)
		self.assertEqual(resp.status, 200)

		data = cjson.decode(data)
		self.assertTrue('pickup' in data)
		self.assertTrue('pickups' in data)
		self.assertTrue('members' in data)
		self.assertEqual(data['pickup'].get('name',''), 'unittest')

	def test_04_delete(self):
		(resp, data) = self.client.delete(self.obj, id=0)
		self.assertEqual(resp.status, 200)

		(resp, data) = self.client.delete(self.obj, id=0)
		self.assertEqual(resp.status, 404)

		(resp, data) = self.client.list(self.obj)
		self.assertEqual(resp.status, 204)

if __name__ == '__main__':
	unittest.main()
