# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
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

from xivo_confgen.backend  import Backend
from xivo_confgen.xivojson import JSONClient

class WSObject(object):
    def __init__(self, iface, name):
        if not name in iface.objects:
            raise AttributeError

        self.iface = iface
        self.name  = name

    def __getattr__(self, action):
        print 'action=', action
        if not action in ['list','add','edit','view','delete']:
            raise AttributeError

        def _q(*args, **kwargs):
            (resp, data) = getattr(self.iface, action)(self.name, *args, **kwargs)
            if resp is None or resp.status != 200:
                return None

            return cjson.decode(data)
        return _q

class XivoWebservicesBackend(Backend):
    def __init__(self):
        self.json = JSONClient('192.168.1.10',username='test',password='test',ssl=False)

    def __getattr__(self, name):
        print 'getattr', name
        return WSObject(self.json, name)
