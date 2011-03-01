# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010-2011  Proformatique <technique@proformatique.com>

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
    def __init__(self, handlers=[]):
        self._opener = urllib2.build_opener(*handlers)
        
    def download(self, url):
        """Open the URL url and return a file-like object."""
        try:
            return self._do_download(url)
        except urllib2.HTTPError, e:
            logger.warning("HTTPError while downloading '%s': %s", self._get_url(url), e)
            if e.code == 401:
                raise InvalidCredentialsError("unauthorized access to '%s'" % self._get_url(url))
            else:
                raise DownloadError(e)
        except urllib2.URLError, e:
            logger.warning("URLError while downloading '%s': %s", self._get_url(url), e)
            raise DownloadError(e)
        
    @staticmethod
    def _get_url(url):
        """Return the URL from either a urllib2.Request or string instance."""
        if hasattr(url, 'get_full_url'):
            return url.get_full_url()
        else:
            return url
    
    def _do_download(self, url):
        """This method is called by the download method. Any urllib2-related exception
        raised in this method will be caught and wrapped around an exception who
        derives from DownloadError. Derived class may override this method if
        needed.
       
        """
        return self._opener.open(url)


class AuthenticatingDownloader(DefaultDownloader):
    def __init__(self, handlers=[]):
        DefaultDownloader.__init__(self, handlers)
        self._pwd_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self._opener.add_handler(urllib2.HTTPBasicAuthHandler(self._pwd_manager))
        self._opener.add_handler(urllib2.HTTPDigestAuthHandler(self._pwd_manager))
        
    def add_password(self, realm, uri, user, passwd):
        self._pwd_manager.add_password(realm, uri, user, passwd)


class RemoteFile(object):
    """A downloadable remote file."""
    _BLOCK_SIZE = 4096
    
    def __init__(self, path, url, downloader, size, hook_factories=[]):
        """
        path -- the destination path (file name) of the file to download
        url -- the URL/object to pass to the downloader
        downloader -- the file downloader
        size -- the size of the file, or None
        """
        # XXX size is not needed in instance of this class, it's just there
        #   for convenience, I wonder if there's a pratical way to get this
        #   information without using the file attribute for remote file....
        self.path = path
        self.url = url
        self.downloader = downloader
        self.size = size
        self.hook_factories = list(hook_factories)
        
    @property
    def filename(self):
        return os.path.basename(self.path)
    
    def exists(self):
        """Return True if the destination path of the file to download refers to
        an existing path.
        
        """
        return os.path.isfile(self.path)
    
    def _download_to_fobj(self, fobj, supp_hooks):
        # fobj is a file-object and is guaranteed NOT to be closed after this
        # method returns.
        hooks = supp_hooks + [factory() for factory in self.hook_factories]
        last_started_idx = 0
        try:
            while last_started_idx < len(hooks):
                hooks[last_started_idx].start()
                last_started_idx += 1
            with contextlib.closing(self.downloader.download(self.url)) as dlfile:
                while True:
                    bytes = dlfile.read(self._BLOCK_SIZE)
                    if not bytes:
                        break
                    for hook in hooks:
                        hook.update(bytes)
                    fobj.write(bytes)
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
                    # hook so that the contract for the other hooks is not
                    # breached
                    hook_idx -= 1
                    try:
                        hooks[hook_idx].fail(e)
                    except Exception:
                        logger.exception('hook.fail raised an exception')
        finally:
            hook_idx = last_started_idx
            while hook_idx:
                hook_idx -= 1
                try:
                    hooks[hook_idx].stop()
                except Exception:
                    logger.exception('hook.stop raised an exception')
    
    def download(self, supp_hooks=[]):
        """Download the file.
        
        Note that it doesn't check if the file already exist or not on the
        filesystem, i.e. it will overwrite the file if it's already there.
        
        Download hooks are stopped in the reverse order they are started.
       
        """
        # XXX usage of a fixed suffix might not be the best idea since we could
        #   overwrite a 'valid' file with this name
        pathname_tmp = self.path + '.tmp'
        try:
            logger.debug('opening temp file')
            outfile = open(pathname_tmp, 'wb')
        except EnvironmentError, e:
            logger.error("error while opening '%s' for write: %s", pathname_tmp, e)
            raise
        else:
            try:
                try:
                    self._download_to_fobj(outfile, supp_hooks)
                finally:
                    logger.debug('closing temp file')
                    outfile.close()
                try:
                    logger.debug('renaming temp file')
                    os.rename(pathname_tmp, self.path)
                except OSError, e:
                    logger.error("error while renaming '%s' to '%s': %s", pathname_tmp, self.path, e)
                    raise
            except Exception:
                logger.debug('error during download')
                # remove temporary download file without modifying the stack trace
                try:
                    raise
                finally:
                    try:
                        logger.debug('removing temp file')
                        os.remove(pathname_tmp)
                    except OSError, e:
                        logger.error("error while removing '%s': %s", pathname_tmp, e)


class DownloadHook(object):
    """Base class for download hooks."""
    def start(self):
        """Called just before the download is started.
        
        If this method returns without raising an exception, this hook is
        guaranteed to have one of it's complete/fail method called and its
        stop method called.
        
        """
        pass
    
    def update(self, arg):
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
        
        This method MUST NOT raise an exception.
        
        """


class SHA1Hook(DownloadHook):
    """Compute the SHA1 sum of a download and check if it match."""
    def __init__(self, sha1sum):
        """
        sha1sum -- the raw sha1 sum (NOT an hex representation).
        """
        self._sha1sum = sha1sum
        
    def start(self):
        self._hash = hashlib.sha1()
    
    def update(self, arg):
        self._hash.update(arg)
    
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
        self._pbar = pbar
        self._size = 0
        
    def start(self):
        self._pbar.start()
        
    def update(self, arg):
        self._size += len(arg)
        self._pbar.update(self._size)
    
    def complete(self):
        self._pbar.finish()


class AbortHook(DownloadHook):
    """Abort a download at will by raising an exception in a call to update."""
    def __init__(self):
        self._abort = False
    
    def update(self, arg):
        if self._abort:
            logger.info('aborting download')
            raise AbortedDownloadError()
    
    def abort_download(self):
        logger.info('scheduling download abortion')
        self._abort = True


def new_downloaders(handlers=[]):
    """Return a 2-items dictionary ret, for which:
    
    ret['default'] is a DefaultDownloader
    ret['auth'] is an AuthenticatingDownloader
    
    """
    auth = AuthenticatingDownloader(handlers)
    default = DefaultDownloader(handlers)
    return {'auth': auth, 'default': default}


def new_handlers(http_proxy=None, ftp_proxy=None):
    """Return a list of handlers to be used by downloaders."""
    supp_handlers = []
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if ftp_proxy:
        proxies['ftp'] = ftp_proxy
    if proxies:
        supp_handlers.append(urllib2.ProxyHandler(proxies))
    return supp_handlers
