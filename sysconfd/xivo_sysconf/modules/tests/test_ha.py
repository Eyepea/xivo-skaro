# -*- coding: utf8 -*-

__license__ = """
    Copyright (C) 2012 Avencall

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

import mock
import os.path
import shutil
import tempfile
import unittest
from StringIO import StringIO
from xivo_sysconf.modules.ha import HAConfigManager, _PostgresConfigUpdater


def new_master_ha_config(slave_ip_address):
    return _new_ha_config('master', slave_ip_address)


def new_slave_ha_config(master_ip_address):
    return _new_ha_config('slave', master_ip_address)


def new_disabled_ha_config():
    return _new_ha_config('disabled', '')


def _new_ha_config(node_type, remote_address):
    return {'node_type': node_type, 'remote_address': remote_address}


class TestHA(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._ha_conf_file = os.path.join(self._tmp_dir, 'test_ha.conf')
        self._ha_config_mgr = HAConfigManager(mock.Mock(), self._ha_conf_file)

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def _create_tmp_conf_file(self, content):
        with open(self._ha_conf_file, 'wb') as fobj:
            fobj.write(content)

    def test_read_conf(self):
        content = """\
{
    "node_type" : "master",
    "remote_address" : "10.0.0.1"
}
"""
        expected_ha_config = new_master_ha_config('10.0.0.1')
        fobj = StringIO(content)

        ha_config = self._ha_config_mgr._read_ha_config_from_fobj(fobj)

        self.assertEqual(expected_ha_config, ha_config)

    def test_write_conf(self):
        ha_config = new_master_ha_config('10.0.0.1')
        expected_content = '{"node_type": "master", "remote_address": "10.0.0.1"}'
        fobj = StringIO()

        self._ha_config_mgr._write_ha_config_to_fobj(ha_config, fobj)

        content = fobj.getvalue()
        self.assertEqual(expected_content, content)

    def test_get_ha_config_no_file(self):
        expected_ha_config = new_disabled_ha_config()

        ha_config = self._ha_config_mgr.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_get_ha_config(self):
        content = """\
{
    "node_type" : "master",
    "remote_address" : "10.0.0.1"
}
"""
        expected_ha_config = new_master_ha_config('10.0.0.1')
        self._create_tmp_conf_file(content)

        ha_config = self._ha_config_mgr.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_update_ha_config(self):
        ha_config = new_master_ha_config('10.0.0.1')

        self._ha_config_mgr.update_ha_config(ha_config, None)

        expected_ha_config = self._ha_config_mgr._read_ha_config()
        self.assertEqual(expected_ha_config, ha_config)


class TestPostgresConfigUpdater(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._pg_hba_filename = os.path.join(self._tmp_dir, _PostgresConfigUpdater.PG_HBA_FILE)
        self._postgresql_filename = os.path.join(self._tmp_dir, _PostgresConfigUpdater.POSTGRESQL_FILE)

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_update_pg_hba_file_from_non_slave_to_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def _new_postgres_updater(self, ha_config):
        return _PostgresConfigUpdater(ha_config, self._tmp_dir)

    def _write_pg_hba_file(self, content):
        self._write_file(self._pg_hba_filename, content)

    def _write_postgresql_file(self, content):
        self._write_file(self._postgresql_filename, content)

    def _write_file(self, filename, content):
        with open(filename, 'w') as fobj:
            fobj.write(content)

    def _read_pg_hba_file(self):
        return self._read_file(self._pg_hba_filename)

    def _read_postgresql_file(self):
        return self._read_file(self._postgresql_filename)

    def _read_file(self, filename):
        with open(filename) as fobj:
            return fobj.read()

    def test_update_pg_hba_file_from_slave_to_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.2/32 trust
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_slave_ha_config('10.0.0.2')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def test_update_pg_hba_file_from_slave_to_non_slave(self):
        pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
host asterisk postgres 10.0.0.1/32 trust
"""
        expected_pg_hba_content = """\
# PostgreSQL Client Authentication Configuration File
local   all         postgres                          ident
host    all             all             127.0.0.1/32            md5
"""
        self._write_pg_hba_file(pg_hba_content)
        ha_config = new_disabled_ha_config()
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_pg_hba_file()

        self.assertEqual(expected_pg_hba_content, self._read_pg_hba_file())

    def test_update_postgresql_file_from_non_slave_to_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
"""
        expected_postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        self._write_postgresql_file(postgresql_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())

    def test_update_postgresql_file_from_slave_to_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        expected_postgresql_content = postgresql_content
        self._write_postgresql_file(postgresql_content)
        ha_config = new_slave_ha_config('10.0.0.1')
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())

    def test_update_postgresql_file_from_slave_to_non_slave(self):
        postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
listen_addresses = '*'
"""
        expected_postgresql_content = """\
# PostgreSQL configuration file
#listen_addresses = 'localhost'     # what IP address(es) to listen on;
"""
        self._write_postgresql_file(postgresql_content)
        ha_config = new_disabled_ha_config()
        postgres_updater = self._new_postgres_updater(ha_config)

        postgres_updater.update_postgresql_file()

        self.assertEqual(expected_postgresql_content, self._read_postgresql_file())
