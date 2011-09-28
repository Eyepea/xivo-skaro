# -*- coding: UTF-8 -*-

import os
import unittest
import shutil
import tempfile
import fetchfw.util as util


def _create_file(base_path, filename, content=None):
    if content is None:
        content = 'test\n'
    abs_filename = os.path.join(base_path, filename)
    with open(abs_filename, 'wb') as fobj:
        fobj.write(content)


def _create_dir(base_path, dirname):
    abs_dirname = os.path.join(base_path, dirname)
    os.mkdir(abs_dirname)


def _create_symlink(base_path, src, linkname):
    abs_src = os.path.join(base_path, src)
    abs_linkname = os.path.join(base_path, linkname)
    os.symlink(abs_src, abs_linkname)


class TestApplySubs(unittest.TestCase):
    def test_no_substitution(self):
        result = util.apply_subs('bar', {})
        self.assertEqual('bar', result)
    
    def test_no_substitution_with_extra_variables(self):
        result = util.apply_subs('bar', {'foo': 'bar'})
        self.assertEqual('bar', result)
    
    def test_no_substitution_with_escape_char(self):
        result = util.apply_subs(r'bar\$', {})
        self.assertEqual('bar$', result)
    
    def test_one_substitution(self):
        result = util.apply_subs('$foo', {'foo': 'bar'})
        self.assertEqual('bar', result)
        
    def test_one_bracket_substitution(self):
        result = util.apply_subs('${foo}', {'foo': 'bar'})
        self.assertEqual('bar', result)
    
    def test_one_substitution_with_text(self):
        result = util.apply_subs('abc $foo xyz', {'foo': 'bar'})
        self.assertEqual('abc bar xyz', result)
    
    def test_one_substitution_with_escape_char(self):
        result = util.apply_subs(r'$foo\$', {'foo': 'bar'})
        self.assertEqual('bar$', result)
    
    def test_multiple_space_separated_substitution(self):
        result = util.apply_subs('$foo1 $foo2', {'foo1': 'bar1',
                                                 'foo2': 'bar2'})
        self.assertEqual('bar1 bar2', result)
    
    def test_multiple_non_space_separated_bracket_substitution(self):
        result = util.apply_subs('$foo1$foo2', {'foo1': 'bar1',
                                                'foo2': 'bar2'})
        self.assertEqual('bar1bar2', result)
    
    def test_missing_substitution_var_raise_error(self):
        self.assertRaises(KeyError, util.apply_subs, '$foolish', {'foo': 'bar'})
    
    def test_substitution_vars_are_case_sensitive(self):
        result = util.apply_subs('$foo $FOO', {'foo': 'bar', 'FOO': 'BAR'})
        self.assertEqual('bar BAR', result)
    
    def test_zero_length_substitution_vars_are_invalid(self):
        self.assertRaises(ValueError, util.apply_subs, ' $ ', {'': 'bar'})

    def test_substitution_value_contains_escape_char(self):
        result = util.apply_subs('$foo', {'foo': r'\$'})
        self.assertEqual(r'\$', result)


class TestCmpVersion(unittest.TestCase):
    TESTS = [('1',      '1',        0),
             ('1.0.0',  '1.0.0',    0),
             ('1.0',    '1.00',     0),
             ('1.1a',   '1.1a',     0),
             ('1',      '1-0',      0),
             ('1-1',    '1-1',      0),
             ('0:1',    '1',        0),
             ('1:1',    '1:1',      0),
             
             ('2',      '1',        1),
             ('1',      '2',        -1),
             
             ('1.0.1',  '1.0.0',    1),
             ('1.0.0',  '1.1.1',    -1),
             
             ('1.10',   '1.2',      1),
             ('1.2',    '1.10',     -1),
             
             ('1',      '1a',       1),
             ('1a',     '1',        -1),
             
             ('1b',     '1a',       1),
             ('1a',     '1b',        -1),
             
             ('1.1',    '1.a',      1),
             ('1.a',    '1.1',      -1),
             
             ('1-1',    '1',        1),
             ('1',      '1-1',      -1),
             
             ('1-10',   '1-2',      1),
             ('1-2',    '1-10',     -1),
             
             ('1:1',    '1',        1),
             ('1',      '1:1',      -1),
             
             ('2:1',    '1:1',      1),
             ('1:1',    '2:1',      -1)]
    
    def test_run_tests_ok(self):
        for version1, version2, result in self.TESTS:
            cmp_result = util.cmp_version(version1, version2)
            if result > 0:
                self.assertTrue(cmp_result > 0, "cmp(%s, %s) == %s, expecting %s"
                                % (version1, version2, cmp_result, result))
            elif result < 0:
                self.assertTrue(cmp_result < 0, "cmp(%s, %s) == %s, expecting %s"
                                % (version1, version2, cmp_result, result))
            else:
                self.assertTrue(cmp_result == 0, "cmp(%s, %s) == %s, expecting %s"
                                % (version1, version2, cmp_result, result))


class TestRecursiveListDir(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_dir, filename, content)
    
    def _create_dir(self, dirname):
        _create_dir(self._tmp_dir, dirname)
    
    def test_empty(self):
        result = sorted(util.recursive_listdir(self._tmp_dir))
        self.assertEqual([], result)
    
    def test_one_file(self):
        self._create_file('file1')
        result = sorted(util.recursive_listdir(self._tmp_dir))
        self.assertEqual(['file1'], result)
    
    def test_one_dir(self):
        self._create_dir('dir1')
        result = sorted(util.recursive_listdir(self._tmp_dir))
        self.assertEqual(['dir1'], result)
    
    def test_one_file_inside_one_dir(self):
        self._create_dir('dir1')
        self._create_file('dir1/file1')
        result = sorted(util.recursive_listdir(self._tmp_dir))
        self.assertEqual(['dir1', 'dir1/file1'], result)


class TestListPaths(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_dir, filename, content)
    
    def _create_dir(self, dirname):
        _create_dir(self._tmp_dir, dirname)
    
    def _create_symlink(self, src, linkname):
        _create_symlink(self._tmp_dir, src, linkname)
    
    def test_empty(self):
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual([], result)
    
    def test_one_file(self):
        self._create_file('file1')
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual(['file1'], result)
    
    def test_one_dir(self):
        self._create_dir('dir1')
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual(['dir1/'], result)

    def test_one_file_and_one_dir(self):
        self._create_dir('dir1')
        self._create_file('file1')
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual(['dir1/', 'file1'], result)
    
    def test_one_file_inside_one_dir(self):
        self._create_dir('dir1')
        self._create_file('dir1/file1')
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual(['dir1/', 'dir1/file1'], result)

    def test_3_level_dir_recursion(self):
        self._create_dir('dir1')
        self._create_dir('dir1/dir2')
        self._create_dir('dir1/dir2/dir3')
        self._create_file('dir1/dir2/dir3/file1')
        result = sorted(util.list_paths(self._tmp_dir))
        self.assertEqual(['dir1/',
                          'dir1/dir2/',
                          'dir1/dir2/dir3/',
                          'dir1/dir2/dir3/file1'],
                          result)


class TestInstallPaths(unittest.TestCase):
    # NOTE: these tests depends on the good behaviour of util.list_paths
    
    def setUp(self):
        self._tmp_src_dir = tempfile.mkdtemp()
        self._tmp_dst_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_src_dir)
        shutil.rmtree(self._tmp_dst_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_src_dir, filename, content)
    
    def _create_dir(self, dirname):
        _create_dir(self._tmp_src_dir, dirname)
    
    def _install(self):
        return sorted(util.install_paths(self._tmp_src_dir, self._tmp_dst_dir))
    
    def test_empty(self):
        result = self._install()
        self.assertEqual([], sorted(util.list_paths(self._tmp_dst_dir)))
        self.assertEqual([], result)
    
    def test_install_one_file(self):
        self._create_file('file1')
        result = self._install()
        self.assertEqual(['file1'], sorted(util.list_paths(self._tmp_dst_dir)))
        self.assertEqual(['file1'], result)
    
    def test_install_one_file_and_one_dir(self):
        self._create_dir('dir1')
        self._create_file('file1')
        result = self._install()
        self.assertEqual(['dir1/', 'file1'], sorted(util.list_paths(self._tmp_dst_dir)))
        self.assertEqual(['dir1/', 'file1'], result)
    
    def test_one_file_inside_one_dir(self):
        self._create_dir('dir1')
        self._create_file('dir1/file1')
        result = self._install()
        self.assertEqual(['dir1/', 'dir1/file1'], sorted(util.list_paths(self._tmp_dst_dir)))
        self.assertEqual(['dir1/', 'dir1/file1'], result)


class TestRemovePaths(unittest.TestCase):
    # NOTE: these tests depends on the good behaviour of util.list_paths
    
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def _create_file(self, filename, content=None):
        _create_file(self._tmp_dir, filename, content)
    
    def _create_dir(self, dirname):
        _create_dir(self._tmp_dir, dirname)
    
    def test_remove_nothing(self):
        result = sorted(util.remove_paths([], self._tmp_dir))
        self.assertEqual([], result)
    
    def test_remove_one_file(self):
        self._create_file('file1')
        result = sorted(util.remove_paths(['file1'], self._tmp_dir))
        self.assertEqual([], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['file1'], result)
    
    def test_remove_one_dir(self):
        self._create_dir('dir1')
        result = sorted(util.remove_paths(['dir1/'], self._tmp_dir))
        self.assertEqual([], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['dir1/'], result)
    
    def test_remove_one_file_remove_file_only(self):
        self._create_file('file1')
        self._create_file('file2')
        result = sorted(util.remove_paths(['file1'], self._tmp_dir))
        self.assertEqual(['file2'], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['file1'], result)
    
    def test_remove_one_dir_remove_dir_only(self):
        self._create_dir('dir1')
        self._create_file('file2')
        result = sorted(util.remove_paths(['dir1/'], self._tmp_dir))
        self.assertEqual(['file2'], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['dir1/'], result)
    
    def test_remove_file_as_dir_fail(self):
        self._create_file('file1')
        # Note the a little bit weird syntax since util.remove_paths returns
        # an iterator that does nothing until we iterate over it
        self.assertRaises(OSError, sorted, util.remove_paths(['file1/'], self._tmp_dir))
    
    def test_remove_dir_as_file_fail(self):
        self._create_dir('dir1')
        self.assertRaises(OSError, sorted, util.remove_paths(['dir1'], self._tmp_dir))
    
    def test_remove_non_empty_dir_doesnt_raise_nor_remove(self):
        self._create_dir('dir1')
        self._create_file('dir1/file1')
        result = sorted(util.remove_paths(['dir1/'], self._tmp_dir))
        self.assertEqual(['dir1/', 'dir1/file1'], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['dir1/'], result)
    
    def test_remove_inexistant_file_doesnt_raise(self):
        result = sorted(util.remove_paths(['file1'], self._tmp_dir))
        self.assertEqual([], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['file1'], result)
    
    def test_remove_inexistant_dir_doesnt_raise(self):
        result = sorted(util.remove_paths(['dir1/'], self._tmp_dir))
        self.assertEqual([], sorted(util.list_paths(self._tmp_dir)))
        self.assertEqual(['dir1/'], result)
