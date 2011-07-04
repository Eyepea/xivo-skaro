# -*- coding: UTF-8 -*-

import os
import shutil
import tempfile
import unittest
import fetchfw.install as install
from fetchfw.util import list_paths 

#TEST_RES_DIR = '../test_resources/install'
TEST_RES_DIR = 'test_resources/install'


def _create_file(base_path, filename, content=None):
    if content is None:
        content = 'test\n'
    abs_filename = os.path.join(base_path, filename)
    with open(abs_filename, 'wb') as fobj:
        fobj.write(content)


def _create_dir(base_path, dirname):
    abs_dirname = os.path.join(base_path, dirname)
    os.mkdir(abs_dirname)


class TestNullSource(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._null_source = install.NullSource()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def test_null_source_ok(self):
        self._null_source.pull(self._tmp_dir)
        self.assertEqual([], os.listdir(self._tmp_dir))


class TestStandardExtractFilter(object):
    # _FILE
    # _FILTER
    
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def test_filter(self):
        filter = self._FILTER(self._FILE)
        filter.apply(TEST_RES_DIR, self._tmp_dir)
        self.assert_output_directory_content()
    
    def assert_output_directory_content(self):
        self.assertEqual(['dir0/',
                          'dir0/file1.txt',
                          'file0.txt'],
                         sorted(list_paths(self._tmp_dir)))


class TestZipFilter(TestStandardExtractFilter, unittest.TestCase):
    _FILE = 'test.zip'
    _FILTER = install.ZipFilter


class TestTarFilter(TestStandardExtractFilter, unittest.TestCase):
    _FILE = 'test.tar'
    _FILTER = install.TarFilter


class TestTgzFilter(TestStandardExtractFilter, unittest.TestCase):
    _FILE = 'test.tgz'
    _FILTER = install.TarFilter


class TestTbz2Filter(TestStandardExtractFilter, unittest.TestCase):
    _FILE = 'test.tbz2'
    _FILTER = install.TarFilter


class TestCiscoUnsignFilter(TestStandardExtractFilter, unittest.TestCase):
    def test_filter(self):
        filter = install.CiscoUnsignFilter('test-fake.sgn', 'test-fake.gz')
        filter.apply(TEST_RES_DIR, self._tmp_dir)
        self.assertEqual(['test-fake.gz'], os.listdir(self._tmp_dir))


class TestExcludeFilter(unittest.TestCase):
    def setUp(self):
        self._tmp_src_dir = tempfile.mkdtemp()
        self._tmp_dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_src_dir)
        shutil.rmtree(self._tmp_dst_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_src_dir, filename, content)
    
    def test_filter(self):
        self._create_file('file1')
        self._create_file('file2')
        filter = install.ExcludeFilter(['file1'])
        filter.apply(self._tmp_src_dir, self._tmp_dst_dir)
        self.assertEqual(['file2'], sorted(list_paths(self._tmp_dst_dir)))


class TestIncludeFilter(unittest.TestCase):
    def setUp(self):
        self._tmp_src_dir = tempfile.mkdtemp()
        self._tmp_dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_src_dir)
        shutil.rmtree(self._tmp_dst_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_src_dir, filename, content)
    
    def test_filter(self):
        self._create_file('file1')
        self._create_file('file2')
        filter = install.IncludeFilter(['file1'])
        filter.apply(self._tmp_src_dir, self._tmp_dst_dir)
        self.assertEqual(['file1'], sorted(list_paths(self._tmp_dst_dir)))


class TestCopyFilter(unittest.TestCase):
    def setUp(self):
        self._tmp_src_dir = tempfile.mkdtemp()
        self._tmp_dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_src_dir)
        shutil.rmtree(self._tmp_dst_dir)
    
    def test_copy_file_to_file_is_ok(self):
        _create_file(self._tmp_src_dir, 'file1')
        filter = install.CopyFilter('file1', 'file')
        filter.apply(self._tmp_src_dir, self._tmp_dst_dir)
        self.assertEqual(['file'], sorted(list_paths(self._tmp_dst_dir)))
    
    def test_copy_files_to_file_raise_error(self):
        _create_file(self._tmp_src_dir, 'file1')
        _create_file(self._tmp_src_dir, 'file2')
        filter = install.CopyFilter(['file1', 'file2'], 'file')
        self.assertRaises(Exception, filter.apply, self._tmp_src_dir, self._tmp_dst_dir)
    
    def test_copy_files_to_dir_is_ok(self):
        _create_file(self._tmp_src_dir, 'file1')
        _create_file(self._tmp_src_dir, 'file2')
        filter = install.CopyFilter(['file1', 'file2'], 'dir/')
        filter.apply(self._tmp_src_dir, self._tmp_dst_dir)
        self.assertEqual(['dir/', 'dir/file1', 'dir/file2'],
                         sorted(list_paths(self._tmp_dst_dir)))
    
    def test_copy_dirs_into_dir_is_ok(self):
        _create_dir(self._tmp_src_dir, 'dir1')
        _create_dir(self._tmp_src_dir, 'dir2')
        filter = install.CopyFilter(['dir1', 'dir2'], 'dir/')
        filter.apply(self._tmp_src_dir, self._tmp_dst_dir)
        self.assertEqual(['dir/', 'dir/dir1/', 'dir/dir2/'],
                         sorted(list_paths(self._tmp_dst_dir)))
    
    def test_copy_dir_into_file_raise_error(self):
        _create_dir(self._tmp_src_dir, 'dir1')
        filter = install.CopyFilter('dir1', 'file1')
        self.assertRaises(Exception, filter.apply, self._tmp_src_dir, self._tmp_dst_dir)
    
    def test_copy_dirs_into_file_raise_error(self):
        _create_dir(self._tmp_src_dir, 'dir1')
        _create_dir(self._tmp_src_dir, 'dir2')
        filter = install.CopyFilter(['dir1', 'dir2'], 'file')
        self.assertRaises(Exception, filter.apply, self._tmp_src_dir, self._tmp_dst_dir)
