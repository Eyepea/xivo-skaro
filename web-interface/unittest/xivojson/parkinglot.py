# -*- coding: utf-8 -*-
"""
    Unittest 01.
    test XiVO WEBI webservices -- incall object
"""
from __future__ import with_statement

__version__ = "$Revision: 8121 $ $Date: 2010-05-14 17:20:24 +0200 (ven. 14 mai 2010) $"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Guillaume Bour, Proformatique

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

class TestParkinglot(unittest.TestCase):
    def setUp(self):
        global IP, PORT, SSL, USERNAME, PASSWORD

        self.client = JSONClient(IP, PORT, SSL, USERNAME, PASSWORD)

    def test_01_parkinglot(self):
        (resp, data) = self.client.list('parkinglot')
        # 204 == no content
        self.assertTrue(resp.status == 200 or resp.status == 204)
        
        if resp.status == 204:
            count = 0
        else:
            data = cjson.decode(data)
#            pprint.pprint(data)
            count = len(data)
				
        # ADD
        content = {
					'name'     : 'unittest', 
					'context'  : 'default',
					'extension': 900,
					'positions': 10,
					'next'     : 0,
					'commented': False,
        }            
        (resp, data) = self.client.add('parkinglot', content)
        self.assertEqual(resp.status, 200)

        id = cjson.decode(data)



        # counting parkinglots
        (resp, data) = self.client.list('parkinglot')
        self.assertTrue(resp.status == 200)
        self.assertEqual(len(cjson.decode(data)), count+1)

        # VIEW
        (resp, data) = self.client.view('parkinglot', id)
        self.assertTrue(resp.status, 200)

        data = cjson.decode(data)
        self.assertEqual(data.get('name',''), 'unittest')
        self.assertEqual(int(data.get('extension',-1)), 900)

 
        # EDIT
        content['extension'] = 800				
        (resp, data) = self.client.edit('parkinglot', content, id=id)
        self.assertTrue(resp.status, 200)

        (resp, data) = self.client.view('parkinglot', id)
        self.assertTrue(resp.status, 200)
        data = cjson.decode(data)

        self.assertEqual(data.get('name','')          , 'unittest')
        self.assertEqual(int(data.get('extension',-1)), 800)
				

        # DELETE	
        (resp, data) = self.client.delete('parkinglot', id)
        self.assertEqual(resp.status, 200)

        # try to redelete => must return 404
        (resp, data) = self.client.delete('parkinglot', id)
        self.assertEqual(resp.status, 404)
	
        # counting parkinglots
        (resp, data) = self.client.list('parkinglot')
        self.assertTrue(resp.status == 200)
        self.assertEqual(len(cjson.decode(data)), count)

        # VIEW #2 (error)
        (resp, data) = self.client.view('parkinglot', id)
        self.assertEqual(resp.status, 404)


if __name__ == '__main__':
    unittest.main()
