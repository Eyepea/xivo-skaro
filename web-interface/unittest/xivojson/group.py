# -*- coding: utf-8 -*-
from __future__ import with_statement

__version__ = "$Revision$ $Date$"
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
import cjson
from xivojson import *

"""REQUIREMENTS:
    - context default with range 200/299 for groups
    - a user with id 1 exists
"""

class Test03Group(XiVOTestCase):
    OBJ = 'groups'

    def setUp(self):
        super(Test03Group, self).setUp()
        self.client.register(self.OBJ, 'service/ipbx', 'pbx_settings')


    def test_01_group(self):
        (resp, data) = self.client.list(self.OBJ)
        # empty list (no groups)
        self.assertEqual(resp.status, 204)

        # ADD
        with open('xivojson/group.json') as f:
            content = cjson.decode(f.read())
        self.debug(content)	

        (resp, data) = self.client.add(self.OBJ, content)
        self.debug(data)
        self.assertEqual(resp.status, 200)

        # LIST / Check add
        (resp, data) = self.client.list(self.OBJ)
        self.assertEqual(resp.status, 200)

        data = cjson.decode(data)
        self.debug(data)

        self.assertEqual(len(data), 1)
        self.assertTrue('name' in data[0])
        self.assertEqual(data[0]['name'], 'unittest')
        
        id = data[0]['id']

        # SEARCH
        (resp, data) = self.client.view(self.OBJ, id)
        self.assertEqual(resp.status, 200)

        data = cjson.decode(data)
        self.debug(data)
        self.assertTrue('groupfeatures' in data)
        self.assertTrue(data['groupfeatures']['number'] == '210')

        # DELETE
        id = data['groupfeatures']['id']
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 200)
        self.debug(data)

        # try to redelete => must return 404
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 404)
        


if __name__ == '__main__':
    unittest.main()
