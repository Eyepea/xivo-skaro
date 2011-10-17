# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2011 Proformatique

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

import subprocess
from xivo.http_json_server import register, CMD_R, HttpReqError

DHCPD_UDPATE_COMMAND = ['dhcpd-update', '-dr']


def dhcpd_update(args, options):
    """Download the latest ISC dhcp server configuration files and
    regenerate the affected configuration files via the dhcpd-update
    command.
    
    """
    try:
        returncode = subprocess.call(DHCPD_UDPATE_COMMAND, close_fds=True)
    except OSError, e:
        raise HttpReqError(500, "error while executing dhcpd-update command", e)
    else:
        if returncode:
            raise HttpReqError(500, "dhcpd-update command returned %s" % returncode)
        else:
            return True


register(dhcpd_update, CMD_R, name='dhcpd_update')
