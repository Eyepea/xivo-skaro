# -*- coding: utf-8 -*-
from __future__ import with_statement

__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Proformatique

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

"""REQUIREMENTS:
    - context default with range 300/399 for queues
    - a user with id 1 exists
"""

class Test05Queue(XiVOTestCase):
    OBJ = 'queues'

    def setUp(self):
        super(Test05Queue, self).setUp()
        self.client.register(self.OBJ, 'callcenter', 'settings')


    def test_01_queue(self):
        (resp, data) = self.client.list(self.OBJ)
        # no queue == code 204
        self.assertEqual(resp.status, 204)

        # ADD
        content = self.jload('xivojson/queue.json')
        self.debug(content)	

        (resp, data) = self.client.add(self.OBJ, content)
        self.debug(data)
        self.assertEqual(resp.status, 200)

        # LIST / Check add
        (resp, data) = self.client.list(self.OBJ)
        self.assertEqual(resp.status, 200)

        data = self.jdecode(data)
        self.debug(data)

        self.assertEqual(len(data), 1)
        self.assertTrue('name' in data[0])
        self.assertTrue(data[0]['name'] == 'unittest')
        
        id = data[0]['id']

        # SEARCH
        (resp, data) = self.client.view(self.OBJ, id)
        self.assertEqual(resp.status, 200)

        data = self.jdecode(data)
        self.debug(data)
        self.assertTrue('queuefeatures' in data)
        self.assertTrue(data['queuefeatures']['number'] == '310')

        # DELETE
        id = data['queuefeatures']['id']
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 200)
        self.debug(data)

        # try to redelete => must return 404
        (resp, data) = self.client.delete(self.OBJ, id)
        self.assertEqual(resp.status, 404)


if __name__ == '__main__':
    unittest.main()
