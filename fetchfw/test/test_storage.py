# -*- coding: UTF-8 -*-

import mock
import os
import tempfile
import unittest
import fetchfw.storage as storage
from ConfigParser import RawConfigParser

#TEST_RES_DIR = '../test_resources/storage'
TEST_RES_DIR = 'test_resources/storage'


class TestDefaultRemoteFileBuilder(unittest.TestCase):
    SECTION = 'test_section'
    SHA1SUM = 'f1d2d2f924e986ac86fdf7b36c94bcdf32beec15'    # fake sha1sum
    DLERS = {'default': 'fake downloader'}
    
    def setUp(self):
        self._cache_dir = tempfile.mkdtemp()
        self._downloaders = {'default': mock.Mock()}
    
    def tearDown(self):
        os.rmdir(self._cache_dir)
    
    def test_ok_on_all_mandatory_parameters_specified(self):
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   self._downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'size', '1')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        
        xfile = builder.build_remote_file(config, self.SECTION)
        self.assertEqual('foo.zip', xfile.filename)
    
    def test_missing_url_raise_error(self):
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   self._downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'size', '1')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        
        self.assertRaises(Exception, builder.build_remote_file, config, self.SECTION)

    def test_missing_size_raise_error(self):
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   self._downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        
        self.assertRaises(Exception, builder.build_remote_file, config, self.SECTION)
    
    def test_missing_sha1sum_raise_error(self):
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   self._downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'size', '1')
        
        self.assertRaises(Exception, builder.build_remote_file, config, self.SECTION)

    def test_specified_filename_override_implicit(self):
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   self._downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'filename', 'bar.zip')
        config.set(self.SECTION, 'size', '1')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        
        xfile = builder.build_remote_file(config, self.SECTION)
        self.assertEqual('bar.zip', xfile.filename)
    
    def test_downloader_is_looked_up_in_dict_if_specified(self):
        downloaders = mock.MagicMock()
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'size', '1')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        config.set(self.SECTION, 'downloader', 'foobar')
        
        builder.build_remote_file(config, self.SECTION)
        downloaders.__getitem__.assert_called_once_with('foobar')
    
    def test_default_downloader_is_looked_up_in_dict_if_unspecified(self):
        downloaders = mock.MagicMock()
        builder = storage.DefaultRemoteFileBuilder(self._cache_dir,
                                                   downloaders)
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'url', 'http://example.org/foo.zip')
        config.set(self.SECTION, 'size', '1')
        config.set(self.SECTION, 'sha1sum', self.SHA1SUM)
        
        builder.build_remote_file(config, self.SECTION)
        downloaders.__getitem__.assert_called_once_with('default')


class TestDefaultFilterBuilder(unittest.TestCase):
    def setUp(self):
        self._builder = storage.DefaultFilterBuilder()
    
    def test_build_null_filter_ok(self):
        self._builder.build_node(['null'])
    
    def test_invalid_argument_null_filter_raise_error(self):
        self.assertRaises(Exception, self._builder.build_node, ['null', 'foo'])
    
    def test_unknown_type_raise_error(self):
        self.assertRaises(Exception, self._builder.build_node, ['foobarfoo'])


class TestDefaultInstallMgrFactory(unittest.TestCase):
    SECTION = 'test_section'
    
    def test_ok_on_valid_section(self):
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'a-b', 'null')
        mgr_factory = storage.DefaultInstallMgrFactory(config, self.SECTION,
                                                       mock.Mock(), {})
        mgr_factory.new_install_mgr(mock.Mock(), {})

    def test_raise_error_on_loop(self):
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'a-b', 'null')
        config.set(self.SECTION, 'b-a', 'null')
        mgr_factory = storage.DefaultInstallMgrFactory(config, self.SECTION,
                                                       mock.Mock(), {})
        self.assertRaises(Exception, mgr_factory.new_install_mgr, mock.Mock(), {})


class TestDefaultInstallMgrFactoryBuilder(unittest.TestCase):
    SECTION = 'test_section'
    
    def test_build_install_mgr_factory_ok(self):
        factory_builder = storage.DefaultInstallMgrFactoryBuilder(mock.Mock(), {})
        config = RawConfigParser()
        config.add_section(self.SECTION)
        config.set(self.SECTION, 'a-b', 'null')
        
        factory = factory_builder.build_install_mgr_factory(config, self.SECTION)
        self.assertTrue(isinstance(factory, storage.DefaultInstallMgrFactory))


class TestDefaultInstallablePkgStorage(unittest.TestCase):
    def setUp(self):
        self._cache_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        os.rmdir(self._cache_dir)
    
    def test_ok_on_valid_db(self):
        db_dir = os.path.join(TEST_RES_DIR, 'installable')
        installable_pkg_sto = storage.new_installable_pkg_storage(
            db_dir, self._cache_dir, {'default': 'default dler'}, {})
        self.assertTrue('simple1' in installable_pkg_sto)
        self.assertTrue('simple2' in installable_pkg_sto)


class TestDefaultInstalledPkgStorage(unittest.TestCase):
    def test_ok_on_valid_db(self):
        db_dir = os.path.join(TEST_RES_DIR, 'installed')
        installed_pkg_sto = storage.new_installed_pkg_storage(db_dir)
        self.assertTrue('simple1' in installed_pkg_sto)


class TestBasePkgStorage(unittest.TestCase):
    def _new_pkg(self, depends=[]):
        pkg = mock.Mock()
        pkg.pkg_info = {'depends': depends}
        return pkg
    
    def test_dependencies_with_maxdepth_0_return_empty_set(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg()}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(set(), pkg_sto.get_dependencies('a', 0))
    
    def test_dependencies_with_maxdepth_1_return_direct_deps(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg(['c']),
                'c': self._new_pkg()}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['b'], sorted(pkg_sto.get_dependencies('a', 1)))
    
    def test_dependencies_return_direct_and_indirect_deps(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg(['c', 'd']),
                'c': self._new_pkg(),
                'd': self._new_pkg(),
                'e': self._new_pkg(),}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['b', 'c', 'd'], sorted(pkg_sto.get_dependencies('a')))
    
    def test_dependencies_multiple_depths_consider_shortest_depth(self):
        pkgs = {'a': self._new_pkg(['c']),
                'b': self._new_pkg(['d']),
                'c': self._new_pkg(['d']),
                'd': self._new_pkg()}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['c', 'd'],
                         sorted(pkg_sto.get_dependencies_many(['a', 'b'], maxdepth=1)))
    
    def test_dependencies_works_fine_with_direct_cycle(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg(['a'])}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['a', 'b'], sorted(pkg_sto.get_dependencies('a')))
    
    def test_dependencies_works_fine_with_indirect_cycle(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg(['c']),
                'c': self._new_pkg(['a'])}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['a', 'b', 'c'], sorted(pkg_sto.get_dependencies('a')))

    def test_dependencies_missing_raise_error_when_not_ignore(self):
        pkgs = {'a': self._new_pkg(['b'])}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertRaises(Exception, pkg_sto.get_dependencies, 'a')
    
    def test_dependencies_missing_ok_when_ignore(self):
        pkgs = {'a': self._new_pkg(['b'])}
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['b'], sorted(pkg_sto.get_dependencies('a', ignore_missing=True)))
    
    def test_dependencies_ok_with_filter_fun(self):
        pkgs = {'a': self._new_pkg(['b']),
                'b': self._new_pkg(['c']),
                'c': self._new_pkg()}
        filter_fun = lambda pkg_id: pkg_id != 'c'
        pkg_sto = storage.BasePkgStorage()
        pkg_sto._pkgs = pkgs
        self.assertEqual(['b'], sorted(pkg_sto.get_dependencies('a', filter_fun=filter_fun)))
