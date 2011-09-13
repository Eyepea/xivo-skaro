# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011 Proformatique'
__author__    = 'Corentin Le Gall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cjson
import httplib

headers = { 'Content-type': 'application/json',
            'Accept': 'text/plain' }

class xws():
    def __init__(self, ipaddress, ipport):
        self.myconn = None
        self.ipaddress = ipaddress
        self.ipport = ipport
        self.path = '/service/ipbx/json.php/private/pbx_settings/users'
        if self.ipaddress not in ['localhost', '127.0.0.1']:
            self.path = '/service/ipbx/json.php/restricted/pbx_settings/users'
        return

    def connect(self):
        if self.ipport == 443:
            self.myconn = httplib.HTTPSConnection(self.ipaddress, self.ipport)
        else:
            self.myconn = httplib.HTTPConnection(self.ipaddress, self.ipport)
        return

    def serviceget(self, userid):
        uri = '%s/?act=view&id=%s' % (self.path, userid)
        pattern = {}
        self.myconn.request('POST', uri, cjson.encode(pattern), headers)
        z = self.myconn.getresponse()
        y = cjson.decode(z.read())
        return y

    def serviceput(self, userid, function, value):
        status = self.serviceget(userid)
        uri = '%s/?act=edit&id=%s' % (self.path, userid)
        userfeatures = status['userfeatures']
        # cjson workaround
        if 'timezone' in userfeatures:
            userfeatures['timezone'] = userfeatures['timezone'].replace('\\/', '/')
        userfeatures[function] = value
        pattern = { 'userfeatures' : userfeatures }
        self.myconn.request('POST', uri, cjson.encode(pattern), headers)
        z = self.myconn.getresponse()
        z.read()
        return

    def close(self):
        self.myconn.close()
