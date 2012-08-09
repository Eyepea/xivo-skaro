# -*- coding: UTF-8 -*-

__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010  Avencall

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

import logging, subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW

logger = logging.getLogger('xivo_sysconf.modules.services')


def services(args, options):
    """
    POST /services

    >>> services({'networking': 'restart'})
    """
    for svc, act in args.iteritems():
        if act not in ['stop', 'start', 'restart']:
            logger.error("action %s not authorized on %s service", act, svc)

        try:
            p = subprocess.Popen(["/etc/init.d/%s" % svc, act],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
            output = p.communicate()[0]
            logger.debug("/etc/init.d/%s %s : %d", svc, act, p.returncode)

            if p.returncode != 0:
                raise HttpReqError(500, output)
        except OSError:
            logger.exception("Error while executing /etc/init.d script")
            raise HttpReqError(500, "can't manage services")

    return output


http_json_server.register(services, CMD_RW, name='services')
