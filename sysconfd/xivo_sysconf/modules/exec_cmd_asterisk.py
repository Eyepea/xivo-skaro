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

import logging, subprocess

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW

logger = logging.getLogger(__name__)


AST_CMD_REQUESTS = [
    'core reload',
    'core restart now',
    'core show version',
    'core show channels',
    'dialplan reload',
    'sccp reload',
    'sip reload',
    'moh reload',
    'iax2 reload',
    'module reload',
    'module reload app_queue.so',
    'module reload chan_agent.so',
    'module reload app_meetme.so',
    'features reload',
    'voicemail reload',
    'module reload chan_sccp.so',
    'sccp show version',
    'sccp show devices',
    'sccp show config',
    'sccp update config',
    ]

def exec_cmd_asterisk(cmd, options):
    """
    POST /exec_cmd_asterisk

    >>> exec_cmd_asterisk(sip reload)
    """
    if cmd in AST_CMD_REQUESTS or cmd.startswith('sip show peer'):
        try:
            p = subprocess.Popen(['asterisk', '-rx', cmd],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)
            output = p.communicate()[0]

            if p.returncode != 0:
                raise HttpReqError(500, output)
            else:
                logger.info("Asterisk command '%s' successfully executed", cmd)
        except OSError:
            logger.exception("Error while executing asterisk command")
            raise HttpReqError(500, "can't manage exec_cmd_asterisk")
        return output
    else:
        logger.error("cmd %s not authorized on", cmd)


http_json_server.register(exec_cmd_asterisk, CMD_RW, name='exec_cmd_asterisk')
