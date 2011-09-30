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
from xivojson import *

class Test04Agent(XiVOTestCase):
    OBJ = 'agents'

    def setUp(self):
        super(Test04Agent, self).setUp()
        self.client.register(self.OBJ, 'callcenter', 'settings')


    def test_01_agent(self):
        (resp, data) = self.client.list(self.OBJ)
        # no agent
        self.assertEqual(resp.status, 204)
        
        # ADD
        content = self.jload('xivojson/agent.json')
        self.debug(content)

        (resp, data) = self.client.add(self.OBJ, content)
        self.debug(data)
        self.assertEqual(resp.status, 200)

        # LIST
        (resp, data) = self.client.list(self.OBJ)
        self.assertEqual(resp.status, 200)

        data = self.jdecode(data)
        self.debug(data)

        self.assertEqual(len(data), 1)
        self.assertTrue('number' in data[0])
        self.assertTrue(data[0]['number'] == '160')
        
        id = data[0]['id']

        # SEARCH
        (resp, data) = self.client.view(self.OBJ, id)
        self.assertEqual(resp.status, 200)

        data = self.jdecode(data)
        self.debug(data)
        self.assertTrue('agentfeatures' in data)
        self.assertTrue(data['agentfeatures']['fullname'] == 'john doe')

        # DELETE
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 200)
        self.debug(data)

        # try to redelete => must return 404
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 404)

if __name__ == '__main__':
    unittest.main()
