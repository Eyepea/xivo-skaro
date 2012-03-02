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
import json

from xivo import http_json_server
from xivo.http_json_server import CMD_R, CMD_RW

logger = logging.getLogger('xivo_sysconf.modules.ha')

HA_CONF_FILE = '/etc/pf-xivo/ha.conf'

DEFAULT_HA_CONFIG = {
    "node_type" : "disabled",
    "remote_address" : ""
}

def get_ha_config(args, options):
    ha_config = _read_ha_config()
    return ha_config


def _read_ha_config():
    try:
        with open(HA_CONF_FILE) as fobj:
            return _read_ha_config_from_fobj(fobj)
    except IOError as e:
        logger.info('could not open %s: %s', HA_CONF_FILE, e)
        return DEFAULT_HA_CONFIG


def _read_ha_config_from_fobj(fobj):
    ret = json.load(fobj)
    return ret


def update_ha_config(args, options):
    ha_config = args
    _write_ha_config(ha_config)


def _write_ha_config(ha_config):
    with open(HA_CONF_FILE, 'wb') as fobj:
        _write_ha_config_from_fobj(ha_config, fobj)


def _write_ha_config_from_fobj(ha_config, fobj):
    json.dump(ha_config, fobj)


http_json_server.register(get_ha_config, CMD_R, name='get_ha_config')
http_json_server.register(update_ha_config, CMD_RW, name='update_ha_config')
