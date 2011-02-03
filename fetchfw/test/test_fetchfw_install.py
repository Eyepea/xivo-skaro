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
import shutil
import tempfile
import unittest

from fetchfw.install import *
from fetchfw.util import *

TEST_RESOURCES_DIR = '../test_resources/install'

class TestExtractFilter(object):
    def setUp(self):
        self._src_dir = TEST_RESOURCES_DIR
        self._dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._dst_dir, True)
        
    def test_filter(self):
        filter = self._FILTER(self._FILENAME)
        filter.apply(self._src_dir, self._dst_dir)
        self.assert_output_directory_content()
        
    def assert_output_directory_content(self):
        self.assertEqual(set(['dir0', 'file0.txt']), set(os.listdir(self._dst_dir)))
        self.assertEqual(set(['file1.txt']), set(os.listdir(os.path.join(self._dst_dir, 'dir0'))))
        
        
class TestZipFilter(TestExtractFilter, unittest.TestCase):
    _FILTER = ZipFilter
    _FILENAME = 'test.zip'


class TestTarFilter(TestExtractFilter, unittest.TestCase):
    _FILTER = TarFilter
    _FILENAME = 'test.tar'


class TestTgzFilter(TestExtractFilter, unittest.TestCase):
    _FILTER = TarFilter
    _FILENAME = 'test.tgz'


class TestTbz2Filter(TestExtractFilter, unittest.TestCase):
    _FILTER = TarFilter
    _FILENAME = 'test.tbz2'


class TestCiscoUnsignFilter(TestExtractFilter, unittest.TestCase):
    def test_filter(self):
        filter = CiscoUnsignFilter('test-fake.sgn', 'test-fake.gz')
        filter.apply(self._src_dir, self._dst_dir)
        self.assertEqual(['test-fake.gz'], os.listdir(self._dst_dir))


class TestExcludeFilter(unittest.TestCase):
    def setUp(self):
        self._src_dir = TEST_RESOURCES_DIR
        self._dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._dst_dir, True)
    
    def test_filter(self):
        filter = ExcludeFilter(['test_dir/txt11.txt', 'txt2.txt', 'test_dir2'])
        filter.apply(self._src_dir, self._dst_dir)
        self.assertEqual(set(['test.tar', 'test.tbz2', 'test.tgz', 'test.zip', 'test-fake.sgn', 'txt1.txt', 'test_dir']),
                         set(f for f in os.listdir(self._dst_dir) if '.svn' not in f))
        self.assertEqual([],
                         [f for f in os.listdir(os.path.join(self._dst_dir, 'test_dir')) if '.svn' not in f])


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self._src_dir = TEST_RESOURCES_DIR
        self._dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._dst_dir, True)
        
    def test_install_doesnt_accept_empty(self):
        self.assertRaises(ValueError, StandardInstaller, [], self._dst_dir)
    
    def test_install_file_into_file(self):
        installer = StandardInstaller('txt1.txt', os.path.join(self._dst_dir, 'txt1.txt.install'))
        files = installer.install(self._src_dir)
        res = set(ends_with(p, '/') for p in explode_path(self._dst_dir) if p != '/')
        res.update(os.path.join(self._dst_dir, file) for file in ['txt1.txt.install'])
        self.assertEqual(res, files)
        self.assertEqual(set(['txt1.txt.install']), set(os.listdir(self._dst_dir)))
    
    def test_install_file_into_files(self):
        installer = StandardInstaller(['txt1.txt', 'txt2.txt'], os.path.join(self._dst_dir, 'txt1.txt.install'))
        self.assertRaises(InstallationError, installer.install, self._src_dir)
    
    def test_install_dir_into_file(self):
        installer = StandardInstaller('test_dir', os.path.join(self._dst_dir, 'test_dir.install'))
        self.assertRaises(InstallationError, installer.install, self._src_dir)
        
    def test_install_dirs_into_file(self):
        installer = StandardInstaller(['test_dir', 'test_dir2'], os.path.join(self._dst_dir, 'test_dir.install'))
        self.assertRaises(InstallationError, installer.install, self._src_dir)

    def test_install_file_into_dir(self):
        installer = StandardInstaller('txt1.txt', os.path.join(self._dst_dir, 'install_rep/'))
        files = installer.install(self._src_dir)
        res = set(ends_with(p, '/') for p in explode_path(self._dst_dir) if p != '/')
        res.update(os.path.join(self._dst_dir, file) for file in ['install_rep/', 'install_rep/txt1.txt'])
        self.assertEqual(res, files)
        self.assertEqual(set(['install_rep']), set(os.listdir(self._dst_dir)))
        self.assertEqual(set(['txt1.txt']), set(os.listdir(os.path.join(self._dst_dir, 'install_rep'))))
    
    def test_install_files_into_dir(self):
        installer = StandardInstaller(['txt1.txt', 'txt2.txt'], os.path.join(self._dst_dir, 'install_rep/'))
        files = installer.install(self._src_dir)
        res = set(ends_with(p, '/') for p in explode_path(self._dst_dir) if p != '/')
        res.update(os.path.join(self._dst_dir, file) for file in
                   ['install_rep/', 'install_rep/txt1.txt', 'install_rep/txt2.txt'])
        self.assertEqual(res, files)
        self.assertEqual(set(['install_rep']), set(os.listdir(self._dst_dir)))
        self.assertEqual(set(['txt1.txt', 'txt2.txt']),
                         set(os.listdir(os.path.join(self._dst_dir, 'install_rep'))))

    def test_install_dir_into_dir(self):
        installer = StandardInstaller('test_dir', os.path.join(self._dst_dir, 'install_rep/'))
        files = installer.install(self._src_dir)
        res = set(ends_with(p, '/') for p in explode_path(self._dst_dir) if p != '/')
        res.update(os.path.join(self._dst_dir, file) for file in
                   ['install_rep/', 'install_rep/test_dir/', 'install_rep/test_dir/txt11.txt'])
        self.assertEqual(res, set(file for file in files if '.svn' not in file ))
        self.assertEqual(set(['install_rep']), set(os.listdir(self._dst_dir)))
        self.assertEqual(set(['test_dir']), set(os.listdir(os.path.join(self._dst_dir, 'install_rep'))))
    
    # skip this test since it's not supported right now
#    def test_install_curdir_into_dir(self):
#        installer = StandardInstaller('.', os.path.join(self._dst_dir, 'install_rep/'))
#        files = installer.install(os.path.join(self._src_dir, 'test_dir'))
#        res = set(ends_with(p, '/') for p in explode_path(self._dst_dir) if p != '/')
#        res.update(os.path.join(self._dst_dir, file) for file in
#                   ['install_rep/', 'install_rep/txt11.txt'])
#        self.assertEqual(res, set(file for file in files if '.svn' not in file ))
#        self.assertEqual(set(['install_rep']), set(os.listdir(self._dst_dir)))
#        self.assertEqual(set(['txt11.txt']), set(os.listdir(os.path.join(self._dst_dir, 'install_rep'))))


