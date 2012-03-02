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

import errno
import json
import os
import subprocess
from xivo import http_json_server
from xivo.http_json_server import CMD_R, CMD_RW


class HAConfigManager(object):
    DEFAULT_HA_CONF_FILE = '/etc/pf-xivo/ha.conf'
    DEFAULT_HA_CONFIG = {
        'node_type': 'disabled',
        'remote_address': ''
    }

    def __init__(self, postgres_config_updater_factory, ha_conf_file=DEFAULT_HA_CONF_FILE):
        self._postgres_config_updater_factory = postgres_config_updater_factory
        self._ha_conf_file = ha_conf_file

    def get_ha_config(self, args, options):
        return self._read_ha_config()

    def _read_ha_config(self):
        try:
            with open(self._ha_conf_file) as fobj:
                return self._read_ha_config_from_fobj(fobj)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return dict(self.DEFAULT_HA_CONFIG)
            else:
                raise

    def _read_ha_config_from_fobj(self, fobj):
        return json.load(fobj)

    def update_ha_config(self, args, options):
        ha_config = args
        self._write_ha_config(ha_config)
        self._update_postgres(ha_config)

    def _write_ha_config(self, ha_config):
        with open(self._ha_conf_file, 'wb') as fobj:
            self._write_ha_config_to_fobj(ha_config, fobj)

    def _write_ha_config_to_fobj(self, ha_config, fobj):
        json.dump(ha_config, fobj)

    def _update_postgres(self, ha_config):
        postgres_updater = self._postgres_config_updater_factory(ha_config)
        postgres_updater.update_pg_hba_file()
        postgres_updater.update_postgresql_file()
        postgres_updater.restart_postgres()


class _PostgresConfigUpdater(object):
    DEFAULT_CONFIG_DIR = '/etc/postgresql/9.0/main'
    PG_HBA_FILE = 'pg_hba.conf'
    POSTGRESQL_FILE = 'postgresql.conf'

    def __init__(self, ha_config, postgres_config_dir=DEFAULT_CONFIG_DIR):
        self._ha_config = ha_config
        self._pg_hba_file = os.path.join(postgres_config_dir, self.PG_HBA_FILE)
        self._postgresql_file = os.path.join(postgres_config_dir, self.POSTGRESQL_FILE)

    def update_pg_hba_file(self):
        self._clear_host_line_in_pg_hba()
        if self._ha_config['node_type'] == 'slave':
            self._append_host_line_in_pg_hba()

    def _clear_host_line_in_pg_hba(self):
        command_args = ['sed', '-i', '/^host asterisk postgres/d', self._pg_hba_file]
        subprocess.check_call(command_args, close_fds=True)

    def _append_host_line_in_pg_hba(self):
        master_ip_address = self._ha_config['remote_address']
        host_line = 'host asterisk postgres %s/32 trust\n' % master_ip_address
        with open(self._pg_hba_file, 'a') as fobj:
            fobj.write(host_line)

    def update_postgresql_file(self):
        self._clear_listen_addresses_line_in_postgresql()
        if self._ha_config['node_type'] == 'slave':
            self._append_listen_addresses_line_in_postgresql()

    def _clear_listen_addresses_line_in_postgresql(self):
        command_args = ['sed', '-i', '/^listen_addresses/d', self._postgresql_file]
        subprocess.check_call(command_args, close_fds=True)

    def _append_listen_addresses_line_in_postgresql(self):
        listen_addresses_line = "listen_addresses = '*'\n"
        with open(self._postgresql_file, 'a') as fobj:
            fobj.write(listen_addresses_line)

    def restart_postgres(self):
        command_args = ['/etc/init.d/postgresql', 'restart']
        subprocess.check_call(command_args, close_fds=True)


ha_config_manager = HAConfigManager(_PostgresConfigUpdater)
http_json_server.register(ha_config_manager.get_ha_config, CMD_R,
                          name='get_ha_config')
http_json_server.register(ha_config_manager.update_ha_config, CMD_RW,
                          name='update_ha_config')
