# -*- coding: UTF-8 -*-

import hashlib
import mock
import os
import shutil
import tempfile
import unittest
import fetchfw.download as download


CONTENT = 'foobar'
CORRUPTED_CONTENT = 'barfoo'


class TestBaseRemoteFile(unittest.TestCase):
    URL = 'dummy_url'
    
    def _new_fobj_mock(self):
        # Note that results in is reverse order (i.e. 'foo' will be returned first)
        results = ['', 'foo']
        def read(size):
            return results.pop()
        
        fobj = mock.Mock()
        fobj.read.side_effect = read
        return fobj
    
    def setUp(self):
        downloader = mock.Mock()
        downloader.download.return_value = self._new_fobj_mock()
        hook = mock.Mock()
        self._downloader = downloader
        self._hook = hook
    
    def test_downloader_is_called_when_hooks_play_nice(self):
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        rfile.download()
        self._downloader.download.assert_called_once_with(self.URL)
    
    def test_hook_start_is_called(self):
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        rfile.download([self._hook])
        self._hook.start.assert_called_once_with()

    def test_hook_complete_called_fail_not_on_download_success(self):
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        rfile.download([self._hook])
        self._hook.complete.assert_called_once_with()
        self._hook.fail.method_calls = []
    
    def test_hook_fail_called_complete_not_on_download_failure(self):
        dummy_exception = Exception('dummy')
        self._hook.update.side_effect = dummy_exception
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        
        self.assertRaises(Exception, rfile.download, [self._hook])
        self._hook.complete.method_calls = []
        self._hook.fail.assert_called_once_with(dummy_exception)
    
    def test_hook_stop_is_called_on_download_success(self):
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        rfile.download([self._hook])
        
        self._hook.stop.assert_called_once_with()
    
    def test_hook_stop_is_called_on_download_failure(self):
        self._hook.update.side_effect = Exception('dummy')
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        
        self.assertRaises(Exception, rfile.download, [self._hook])
        self._hook.stop.assert_called_once_with()

    def test_hook_stop_not_called_if_started_not_called(self):
        raise_hook = mock.Mock()
        raise_hook.start.side_effect = Exception('dummy')
        rfile = download.BaseRemoteFile(self.URL, self._downloader)
        
        self.assertRaises(Exception, rfile.download, [raise_hook, self._hook])
        self._hook.stop.method_calls = []


class TestWriteToFileHook(unittest.TestCase):
    FILENAME = 'file.bin'
    
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self._filename = os.path.join(self._tmp_dir, self.FILENAME)
        self._hook = download.WriteToFileHook(self._filename)
        self._hook.start()
    
    def tearDown(self):
        shutil.rmtree(self._tmp_dir)
    
    def _read_file_content(self):
        with open(self._filename, 'rb') as fobj:
            return fobj.read()
    
    def test_file_content_is_ok(self):
        self._hook.update(CONTENT)
        self._hook.complete()
        self._hook.stop()
        self.assertEqual(CONTENT, self._read_file_content())

    def test_only_one_file_created_on_ok(self):
        self._hook.update(CONTENT)
        self._hook.complete()
        self._hook.stop()
        self.assertEqual([self.FILENAME], os.listdir(self._tmp_dir))
    
    def test_no_file_created_on_fail(self):
        self._hook.update(CONTENT)
        self._hook.fail(Exception('dummy'))
        self._hook.stop()
        self.assertEqual([], os.listdir(self._tmp_dir))
    
    def test_factory_class(self):
        # this test look into private attribute of the instance, so if it
        # breaks, check if the private attribute have not changed
        hook_factory = download.WriteToFileHook.create_factory(self.FILENAME)
        hook = hook_factory()
        self.assertTrue(isinstance(hook, download.WriteToFileHook))
        self.assertEqual(hook._filename, self.FILENAME)


class TestSHA1Hook(unittest.TestCase):
    def setUp(self):
        hash = hashlib.sha1()
        hash.update(CONTENT)
        self._sha1sum = hash.digest()
        self._hook = download.SHA1Hook(self._sha1sum)
        self._hook.start()
    
    def tearDown(self):
        self._hook.stop()
    
    def test_doesnt_raise_error_on_ok_data(self):
        self._hook.update(CONTENT)
        self._hook.complete()
    
    def test_doesnt_raise_error_on_ok_splitted_data(self):    
        mid = len(CONTENT) / 2
        self._hook.update(CONTENT[:mid])
        self._hook.update(CONTENT[mid:])
        self._hook.complete()

    def test_doesnt_raise_error_on_external_fail(self):    
        self._hook.update('foo')
        self._hook.fail(Exception('dummy'))
    
    def test_raise_error_on_corrupted_data(self):
        self._hook.update(CORRUPTED_CONTENT)
        self.assertRaises(Exception, self._hook.complete)
    
    def test_factory_class(self):
        # this test look into private attribute of the instance, so if it
        # breaks, check if the private attribute have not changed
        hook_factory = download.SHA1Hook.create_factory(self._sha1sum)
        hook = hook_factory()
        self.assertTrue(isinstance(hook, download.SHA1Hook))
        self.assertEqual(hook._sha1sum, self._sha1sum)


class TestAbortHook(unittest.TestCase):
    def setUp(self):
        self._hook = download.AbortHook()
        self._hook.start()
    
    def tearDown(self):
        self._hook.stop()
    
    def test_abort_ok(self):
        self._hook.abort_download()
        self.assertRaises(download.AbortedDownloadError, self._hook.update, 'foo')
        self._hook.fail(Exception('dummy'))


class TestHelperFunctions(unittest.TestCase):
    def test_new_downloaders_has_correct_keys(self):
        dlers = download.new_downloaders()
        dlers.pop('auth')
        dlers.pop('default')
        self.assertFalse(dlers)
    
    def test_new_downloaders_from_handlers_has_correct_keys(self):
        dlers = download.new_downloaders()
        dlers.pop('auth')
        dlers.pop('default')
        self.assertFalse(dlers)
