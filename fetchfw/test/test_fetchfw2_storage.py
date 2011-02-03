# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010  Proformatique <technique@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import unittest
import tempfile

import fetchfw2.storage as storage

TEST_RESOURCES_DIR = '../test_resources/storage'
TEST_INSTALLABLE_DIR = '../test_resources/storage/installable'
TEST_INSTALLED_DIR = '../test_resources/storage/installed'


class MagicDict(object):
    def __getitem__(self, key):
        return None


class TestDefaultInstallablePkgStorage(unittest.TestCase):
    def test_does_not_lamely_crash(self):
        installable_dict = storage.DefaultInstallablePkgStorage(TEST_INSTALLABLE_DIR,
                                                                 tempfile.gettempdir(),
                                                                 storage.RemoteFileBuilder(MagicDict()),
                                                                 storage.InstallationMgrBuilder(),
                                                                 {})
        self.assertEqual(set(['simple1', 'simple2']), set(installable_dict))


class TestDefaultInstalledPkgStorage(unittest.TestCase):
    def test_does_not_lamely_crash(self):
        installed_dict = storage.DefaultInstalledPkgStorage(TEST_INSTALLED_DIR)
        self.assertEqual(set(['simple1']), set(installed_dict))


class TestSimpleFormatParser(unittest.TestCase):
    def test_parse_simple1(self):
        parser = storage._SimpleFormatParser(os.path.join(TEST_RESOURCES_DIR, 'valid.txt'))
        self.assertEqual(['value1'], parser.get_as_list('section1'))
        self.assertEqual([], parser.get_as_list('section2'))
        self.assertEqual(['value1', 'value2', 'value3'], parser.get_as_list('section3'))
        self.assertEqual('value1', parser.get_as_string('section1'))
        self.assertEqual(None, parser.get_as_string('section2'))
        self.assertEqual('value1', parser.get_as_string('section3'))

    def test_parse_invalid(self):
        self.assertRaises(storage.ParsingError, storage._SimpleFormatParser, os.path.join(TEST_RESOURCES_DIR, 'invalid.txt'))

