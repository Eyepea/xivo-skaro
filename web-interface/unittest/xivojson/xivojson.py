#!/usr/bin/python


__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Guillaume Bour, Proformatique

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

import httplib, urllib, base64, pprint, unittest, os
import cjson as json
# define global variables
from globals  import *

class XiVOTestCase(unittest.TestCase):
    def setUp(self):
        global IP, PORT, SSL, USERNAME, PASSWORD
        self._debug  = os.environ.get('DEBUG', '0') != '0'

        self.client = JSONClient(IP, PORT, SSL, USERNAME, PASSWORD, self._debug)

    def debug(self, obj):
        if not self._debug:
            return

        pprint.pprint(obj)

    def jload(self, jfile):
        with open(jfile) as f:
            content = json.decode(f.read())

        return content

    def jdecode(self, stream):
        return json.decode(stream)


class JSONClient(object):
    objects = {
        'entity'        : ['xivo/configuration'      , 'manage'],
        'users'         : ['service/ipbx'            , 'pbx_settings'],
        'incall'        : ['service/ipbx'            , 'call_management'],
        'pickup'        : ['service/ipbx'            , 'call_management'],

        'queueskill'    : ['service/ipbx'            , 'call_center'],
        'queueskillrules': ['service/ipbx'            , 'call_center'],
        'agents'        : ['service/ipbx'            , 'call_center'],

        'parkinglot'    : ['service/ipbx'            , 'pbx_services'],
        
        'mail'          : ['xivo/configuration'      , 'network'],
        'dhcp'          : ['xivo/configuration'      , 'network'],
        'monitoring'    : ['xivo/configuration'      , 'support'],
    }

    def __init__(self, ip='localhost', port=80, ssl=False, username=None,
            password=None, debug=False):
        self.headers = {
            "Content-type": "application/json",
            "Accept": "text/plain"
        }
        
        if username is not None:
            self.headers['Authorization'] = 'Basic ' + \
                base64.encodestring('%s:%s' % (username, password))[:-1]
        self.baseuri  = '/%s/json.php/restricted/%s/%s/?act=%s'
        
        if ssl:
            self.conn = httplib.HTTPSConnection(ip, port)
        else:
            self.conn = httplib.HTTPConnection(ip, port)

        self._debug = debug

    def debug(self, o):
        if not self._debug:
            return

        pprint.pprint(o)

    def register(self, obj, base, section):
        self.objects[obj] = (base, section)
        
    def request(self, method, uri, params=None):
        if method == 'POST':
            params = json.encode(params)
        elif params:
            mark   = '&' if '?' in uri else '?'
            uri    = "%s%s%s" % (uri, mark, urllib.urlencode(params))
            params = None

        self.debug('request= '+uri)
        self.conn.request(method, uri, params, self.headers)
        response = self.conn.getresponse()
        data     = response.read()
        
        return (response, data)
        
    def list(self, obj):
        if obj not in self.objects:
            raise Exception('Unknown %s object' % obj)
         
        params = self.objects[obj]
        return self.request('GET', 
            self.baseuri % (params[0], params[1], obj, 'list')
        )
        
    def add(self, obj, content):
        if obj not in self.objects:
            raise Exception('Unknown %s object' % obj)
         
        params = self.objects[obj]
        return self.request('POST', 
            self.baseuri % (params[0], params[1], obj, 'add'), 
            content
        )

    def edit(self, obj, content, id=None):
        if obj not in self.objects:
            raise Exception('Unknown %s object' % obj)
         
        params = self.objects[obj]
        uri = self.baseuri % (params[0], params[1], obj, 'edit')
        # kuick ack to support edit urls requiring id parameter
        if id is not None:
            uri += '&id='+id					

        return self.request('POST', 
            uri,
            content
        )

    def view(self, obj, id):
        if obj not in self.objects:
            raise Exception('Unknown %s object' % obj)
         
        params = self.objects[obj]
        return self.request('GET', 
            self.baseuri % (params[0], params[1], obj, 'view'), 
            {'id': id}
        )
        
    def delete(self, obj, id):
        if obj not in self.objects:
            raise Exception('Unknown %s object' % obj)
         
        params = self.objects[obj]
        return self.request('GET', 
            self.baseuri % (params[0], params[1], obj, 'delete'), 
            {'id': id}
        )



