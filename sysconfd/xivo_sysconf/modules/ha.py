# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2012  Avencall

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

import logging

from xivo import http_json_server
from xivo.http_json_server import CMD_R

logger = logging.getLogger('xivo_sysconf.modules.ha')


def ha(args, options):
    return {'uuid': 'lol'}


def set_conf():
    pass


def get_conf():
    pass


http_json_server.register(ha, CMD_R, name='ha')
