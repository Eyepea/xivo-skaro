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
import unittest, cjson, pprint, os
import sysconfd_client

class TestXivo(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	def test_01_delVoicemail(self):
		# creating fake voicemail
		base = '/var/spool/asterisk/voicemail/default/xx_unittest'
		try:
			os.makedirs(base+'/subdir')
		except:
			pass
		open(base+'/AAA','w').close()
		open(base+'/subdir/BBB','w').close()

		(resp, data) = self.client.request('GET', '/delete_voicemail', {})
		self.assertEqual(resp.status, 400)

		(resp, data) = self.client.request('GET', '/delete_voicemail', {'name': 'xx_unittest'})
		self.assertEqual(resp.status, 200)
		self.assertFalse(os.path.exists(base))
		self.assertFalse(os.path.exists(base+'/AAA'))

		(resp, data) = self.client.request('GET', '/delete_voicemail', {'name': 'xx_unittest'})
		self.assertEqual(resp.status, 404)

		# context other than default
		base = '/var/spool/asterisk/voicemail/foobar/xx_unittest'
		try:
			os.makedirs(base+'/subdir')
		except:
			pass
		open(base+'/AAA','w').close()
		open(base+'/subdir/BBB','w').close()

		(resp, data) = self.client.request('GET', '/delete_voicemail', {})
		self.assertEqual(resp.status, 400)

		(resp, data) = self.client.request('GET', '/delete_voicemail', {'name': 'xx_unittest'})
		self.assertEqual(resp.status, 404)

		(resp, data) = self.client.request('GET', '/delete_voicemail', {
			'name': 'xx_unittest', 
			'context': 'foobar'
		})
		self.assertEqual(resp.status, 200)
		self.assertFalse(os.path.exists(base))
		self.assertFalse(os.path.exists(base+'/AAA'))

		(resp, data) = self.client.request('GET', '/delete_voicemail', {
			'name': 'xx_unittest',
			'context': 'foobar'
		})
		self.assertEqual(resp.status, 404)


if __name__ == '__main__':
	unittest.main()
