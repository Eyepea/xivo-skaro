# -*- coding: utf8 -*-

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

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_R

class Xivo(object):
    def __init__(self):
        super(Xivo, self).__init__()

        http_json_server.register(self.uuid, CMD_R,
                        name='xivo_uuid', safe_init=self.safe_init)

    def safe_init(self, options):
        pass

    def uuid(self, args, options):
        """Return UUID (file /usr/share/pf-xivo/XIVO-UUID)"""
        try:
            with open('/usr/share/pf-xivo/XIVO-UUID') as f:
                uuid = f.read()[:-1]
        except:
            raise HttpReqError(500, "cannot read xivo uuid", json=True)

        return {'uuid': uuid}

xivosys = Xivo()
