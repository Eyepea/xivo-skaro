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

import os.path
import shutil
import tempfile
import unittest

import xivo_sysconf.modules.ha as ha
from StringIO import StringIO

class TestHA(unittest.TestCase):
    def setUp(self):
        self.old_ha_conf_file = ha.HA_CONF_FILE
        self._tmp_dir = tempfile.mkdtemp()
        ha.HA_CONF_FILE = os.path.join(self._tmp_dir, 'test_ha.conf')

    def tearDown(self):
        ha.HA_CONF_FILE = self.old_ha_conf_file
        shutil.rmtree(self._tmp_dir)

    def _create_tmp_conf_file(self, content):
        with open(ha.HA_CONF_FILE, 'wb') as fobj:
            fobj.write(content)

    def test_read_conf(self):
        content = \
        """{
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }"""
        expected_ha_config = {
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }
        fobj = StringIO(content)

        ha_config = ha._read_ha_config_from_fobj(fobj)

        self.assertEqual(expected_ha_config, ha_config)

    def test_write_conf(self):
        ha_config = {
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }
        expected_content = '{"node_type": "master", "remote_address": "10.0.0.1"}'
        fobj = StringIO()

        ha._write_ha_config_to_fobj(ha_config, fobj)

        content = fobj.getvalue()
        self.assertEqual(expected_content, content)

    def test_get_ha_config_no_file(self):
        expected_ha_config = {
            "node_type" : "disabled",
            "remote_address" : ""
        }

        ha_config = ha.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_get_ha_config(self):
        content = \
        """{
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }"""
        expected_ha_config = {
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }
        self._create_tmp_conf_file(content)

        ha_config = ha.get_ha_config(None, None)

        self.assertEqual(expected_ha_config, ha_config)

    def test_update_ha_config(self):
        ha_config = {
            "node_type" : "master",
            "remote_address" : "10.0.0.1"
        }

        ha.update_ha_config(ha_config, None)

        expected_ha_config = ha._read_ha_config()
        self.assertEqual(expected_ha_config, ha_config)
