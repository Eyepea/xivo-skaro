# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2010-2011  Avencall

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

import contextlib
import hashlib
import logging
import os
import urllib2
from binascii import b2a_hex
from fetchfw.util import FetchfwError

logger = logging.getLogger(__name__)


class DownloadError(FetchfwError):
    pass


class InvalidCredentialsError(DownloadError):
    pass


class CorruptedFileError(DownloadError):
    pass


class AbortedDownloadError(DownloadError):
    pass


class DefaultDownloader(object):
    _TIMEOUT = 15.0

    def __init__(self, handlers=None):
        if handlers is None:
            self._opener = urllib2.build_opener()
        else:
            self._opener = urllib2.build_opener(*handlers)

    def download(self, url, timeout=_TIMEOUT):
        """Open the URL url and return a file-like object."""
        try:
            return self._do_download(url, timeout)
        except urllib2.HTTPError, e:
            logger.warning("HTTPError while downloading '%s': %s", self._get_url(url), e)
            if e.code == 401:
                raise InvalidCredentialsError("unauthorized access to '%s'" % self._get_url(url))
            else:
                raise DownloadError(e)
        except urllib2.URLError, e:
            logger.warning("URLError while downloading '%s': %s", self._get_url(url), e)
            raise DownloadError(e)

    def _get_url(self, url):
        # Return the URL from either a urllib2.Request or string instance
        if hasattr(url, 'get_full_url'):
            return url.get_full_url()
        else:
            return url

    def _do_download(self, url, timeout):
        """This method is called by the download method. Any urllib2-related exception
        raised in this method will be caught and wrapped around an exception who
        derives from DownloadError. Derived class may override this method if
        needed.
       
        """
        return self._opener.open(url, timeout=timeout)


class AuthenticatingDownloader(DefaultDownloader):
    def __init__(self, handlers=None):
        DefaultDownloader.__init__(self, handlers)
        self._pwd_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self._opener.add_handler(urllib2.HTTPBasicAuthHandler(self._pwd_manager))
        self._opener.add_handler(urllib2.HTTPDigestAuthHandler(self._pwd_manager))

    def add_password(self, realm, uri, user, passwd):
        # Note that if the realm and uri are the same that for an already
        # added user/passwd, it will be replaced by the new value
        self._pwd_manager.add_password(realm, uri, user, passwd)


class BaseRemoteFile(object):
    """A remote file that can be downloaded."""
    _BLOCK_SIZE = 4096

    def __init__(self, url, downloader, hook_factories=None):
        """
        url -- the URL/object to pass to the downloader
        downloader -- the file downloader
        hook_factories -- a list of callable objects that return download hook
        
        """
        self._url = url
        self._downloader = downloader
        if hook_factories is None:
            self._hook_factories = []
        else:
            self._hook_factories = list(hook_factories)

    def download(self, supp_hooks=[]):
        """Download the file and run it through the hooks.
        
        Download hooks are stopped in the reverse order they are started.
        
        """
        logger.debug('Downloading %s', self._url)
        hooks = supp_hooks + [factory() for factory in self._hook_factories]
        last_started_idx = 0
        try:
            while last_started_idx < len(hooks):
                hooks[last_started_idx].start()
                last_started_idx += 1
            with contextlib.closing(self._downloader.download(self._url)) as dlfile:
                while True:
                    data = dlfile.read(self._BLOCK_SIZE)
                    if not data:
                        break
                    for hook in hooks:
                        hook.update(data)
            for hook in reversed(hooks):
                hook.complete()
        except Exception, e:
            # preserve traceback info
            try:
                raise
            finally:
                hook_idx = last_started_idx
                while hook_idx:
                    # Although hook.fail MUST NOT raise an exception, catch
                    # any exception that could be raised from badly implemented
                    # hook so that the contract for the other hooks is respected
                    hook_idx -= 1
                    try:
                        hooks[hook_idx].fail(e)
                    except Exception:
                        logger.error('hook.fail raised an exception', exc_info=True)
        finally:
            hook_idx = last_started_idx
            while hook_idx:
                hook_idx -= 1
                try:
                    hooks[hook_idx].stop()
                except Exception:
                    logger.error('hook.stop raised an exception', exc_info=True)


class RemoteFile(object):
    """A BaseRemoteFile with a few extra attributes:
    
    size -- the size of the remote file
    filename -- the filename of the file that will be written to the filesystem
    path -- the complete path of the file that will be written to the filesystem
    exists -- a method that returns true if the remote file exists on the filesystem
    
    """
    def __init__(self, path, size, base_remote_file):
        """
        path -- the path where the file will be written
        
        Note that you probably want to use the "new_remote_file" function
        instead of directly using this constructor.
        
        """
        self.path = path
        self.size = size
        self._base_remote_file = base_remote_file

    @property
    def filename(self):
        return os.path.basename(self.path)

    def exists(self):
        """Return True if the destination path of the file to download refers to
        an existing path.
        
        """
        return os.path.isfile(self.path)

    def download(self, supp_hooks=[]):
        self._base_remote_file.download(supp_hooks)

    @classmethod
    def new_remote_file(cls, path, size, url, downloader, hook_factories=[]):
        hook_factories = hook_factories + [WriteToFileHook.create_factory(path)]
        base_remote_file = BaseRemoteFile(url, downloader, hook_factories)
        return cls(path, size, base_remote_file)


class DownloadHook(object):
    """Base class for download hooks."""
    def start(self):
        """Called just before the download is started.
        
        If this method returns without raising an exception, this hook is
        guaranteed to have one of it's complete/fail method called and its
        stop method called.
        
        """
        pass

    def update(self, data):
        """Called every time a certain amount of data from the download is
        received.
        
        """
        pass

    def complete(self):
        """Called just after the download has completed.
        
        An exception MAY be raised if this hook consider the download not to
        have successfully completed.
        
        """
        pass

    def fail(self, exc_value):
        """Called just after the download has failed.
        
        exc_value is the exception that caused the download to fail.
        
        Note that this method can be called even if the complete method has
        been called earlier. This happens if another hook in the chain decided
        that the download was in fact not complete.
        
        This method MUST NOT raise an exception.
        
        """
        pass

    def stop(self):
        """Called just after the download is stopped, either because the
        download completed succesfully or failed.
        
        This method is always called if the method 
        
        This method MUST NOT raise an exception.
        
        """
        pass


class WriteToFileHook(DownloadHook):
    """Write a download to a file."""
    def __init__(self, filename):
        DownloadHook.__init__(self)
        self._filename = filename
        # XXX usage of a fixed suffix might not be the best idea since we could
        #     overwrite a 'valid' file with this name, that said we want both files
        #     to be on the same filesystem so that rename are atomic...
        self._tmp_filename = filename + '.tmp'
        self._fobj = None
        self._renamed = False

    def start(self):
        self._fobj = open(self._tmp_filename, 'wb')

    def update(self, data):
        self._fobj.write(data)

    def complete(self):
        self._fobj.close()
        os.rename(self._tmp_filename, self._filename)
        self._renamed = True

    def fail(self, exc_value):
        # note that self._fobj.close() might have already been called since
        # fail can sometimes be called after complete, but this is not a problem
        self._fobj.close()
        # remove temporary file without modifying the stack trace
        try:
            pass
        finally:
            try:
                if self._renamed:
                    filename = self._filename
                else:
                    filename = self._tmp_filename
                os.remove(filename)
            except OSError, e:
                logger.error("error while removing '%s': %s", filename, e)

    @classmethod
    def create_factory(cls, filename):
        """Create a hook factory that will return WriteToFileHook instances."""
        def aux():
            return cls(filename)
        return aux


class SHA1Hook(DownloadHook):
    """Compute the SHA1 sum of a download and check if it match."""
    def __init__(self, sha1sum):
        """
        sha1sum -- the raw sha1 sum (NOT an hex representation).
        """
        DownloadHook.__init__(self)
        self._sha1sum = sha1sum
        self._hash = None

    def start(self):
        self._hash = hashlib.sha1()

    def update(self, data):
        self._hash.update(data)

    def complete(self):
        sha1sum = self._hash.digest()
        if sha1sum != self._sha1sum:
            raise CorruptedFileError("sha1sum mismatch: %s instead of %s" %
                                     (b2a_hex(sha1sum), b2a_hex(self._sha1sum)))

    @classmethod
    def create_factory(cls, sha1sum):
        """Create a hook factory that will return SHA1Hook instances."""
        def aux():
            return cls(sha1sum)
        return aux


class ProgressBarHook(DownloadHook):
    """Update a progress bar matching the download status."""
    def __init__(self, pbar):
        DownloadHook.__init__(self)
        self._pbar = pbar
        self._size = 0

    def start(self):
        self._pbar.start()

    def update(self, data):
        self._size += len(data)
        self._pbar.update(self._size)

    def complete(self):
        self._pbar.finish()


class AbortHook(DownloadHook):
    """Abort a download at will by raising an exception in a call to update."""
    def __init__(self):
        DownloadHook.__init__(self)
        self._abort = False

    def update(self, data):
        if self._abort:
            logger.info('explicitly aborting download')
            raise AbortedDownloadError()

    def abort_download(self):
        logger.info('scheduling download abortion')
        self._abort = True


def new_handlers(proxies=None):
    """Return a list of standard handlers to be used by downloaders.
    
    proxies -- a dictionary mapping protocol names to URLs of proxies, or
      None
    
    """
    if proxies:
        return [urllib2.ProxyHandler(proxies)]
    else:
        return []


def new_downloaders_from_handlers(handlers=None):
    """Return a 2-items dictionary ret, for which:
    
    ret['default'] is a DefaultDownloader
    ret['auth'] is an AuthenticatingDownloader
    
    """
    auth = AuthenticatingDownloader(handlers)
    default = DefaultDownloader(handlers)
    return {'auth': auth, 'default': default}


def new_downloaders(proxies=None):
    """Create standard handlers and downloaders and return a 2-items
    dictionary ret, for which:
    
    ret['default'] is a DefaultDownloader
    ret['auth'] is an AuthenticatingDownloader
    
    """
    return new_downloaders_from_handlers(new_handlers(proxies))
