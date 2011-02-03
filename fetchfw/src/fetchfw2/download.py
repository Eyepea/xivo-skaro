# -*- coding: UTF-8 -*-

from __future__ import with_statement

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

import contextlib
import hashlib
import logging
import os
import urllib2
from fetchfw2.util import FetchfwError

logger = logging.getLogger(__name__)


class DownloadError(FetchfwError):
    pass


class InvalidCredentialsError(DownloadError):
    pass


class CorruptedFileError(DownloadError):
    pass


class FilePermissionDownloadError(DownloadError):
    pass


class DefaultDownloader(object):
    def __init__(self, handlers):
        self._opener = urllib2.build_opener(*handlers)
        
    def download(self, url):
        """Open the URL url and return a file-like object."""
        try:
            return self._do_download(url)
        except urllib2.HTTPError, e:
            logger.exception("HTTPError - download '%s'", self._get_url(url))
            if e.code == 401:
                raise InvalidCredentialsError("unauthorized access to '%s'" % self._get_url(url))
            else:
                raise DownloadError(e)
        except urllib2.URLError, e:
            logger.exception("URLError - download '%s'", self._get_url(url))
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
           raised in this method will be catched and wrapped around an exception who
           derives from DownloadError. Derived class should override this method if
           needed.
        """
        return self._opener.open(url)


class AuthenticatingDownloader(DefaultDownloader):
    def __init__(self, handlers):
        DefaultDownloader.__init__(self, handlers)
        self._pwd_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self._opener.add_handler(urllib2.HTTPBasicAuthHandler(self._pwd_manager))
        self._opener.add_handler(urllib2.HTTPDigestAuthHandler(self._pwd_manager))
        
    def add_password(self, realm, uri, user, passwd):
        self._pwd_manager.add_password(realm, uri, user, passwd)


class RemoteFile(object):
    """A downloadable remote file."""
    _BLOCK_SIZE = 4096
    
    def __init__(self, path, url, downloader, size, hook_factories=()):
        """-path is the destination path (file name) of the file to download
           -url is the URL/object to pass to the downloader
           -downloader is the one responsible to return a fobj from the url
           -size is the size of the file
        """
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
    
    def download(self, supp_hooks=()):
        """Download the file.
        
           Note that it doesn't check if the file already exist or not, i.e. it
           will overwrite the file if it's already there.
        """
        pathname_tmp = self.path + '.tmp'
        try:
            try:
                outfile = open(pathname_tmp, 'wb')
            except OSError, e:
                logger.exception("could not create tmp dl file '%s'", pathname_tmp)
                raise FilePermissionDownloadError("error: couldn't create tmp destination file '%s': %s" % (pathname_tmp, e))
            else:
                try:
                    hooks = [factory() for factory in self.hook_factories]
                    hooks.extend(supp_hooks)
                    with contextlib.closing(self.downloader.download(self.url)) as dlfile:
                        # XXX we might want to start the hooks before the self.downloader.download(self.url)
                        for hook in hooks:
                            hook.start()
                        try:
                            while True:
                                bytes = dlfile.read(self._BLOCK_SIZE)
                                if not bytes:
                                    break
                                for hook in hooks:
                                    hook.update(bytes)
                                outfile.write(bytes)
                            for hook in hooks:
                                hook.finish()
                        finally:
                            for hook in hooks:
                                hook.close()
                finally:
                    outfile.close()
            try:
                os.rename(pathname_tmp, self.path)
            except OSError, e:
                logger.exception("could not rename file '%s' to '%s'", pathname_tmp, self.path)
                raise FilePermissionDownloadError("error: couldn't create destination file '%s': %s" % (self.path, e))
            assert not os.path.isfile(pathname_tmp)
        except Exception:
            try:
                raise
            finally:
                try:
                    os.remove(pathname_tmp)
                except OSError:
                    logger.debug("could not remove tmpfile '%s' (it may be normal)", pathname_tmp, exc_info=True)


class Hook(object):
    def close(self):
        pass
    
    def finish(self):
        """Note that this method is not called if the download doesn't complete. """
        pass
    
    def start(self):
        pass
    
    def update(self, arg):
        pass


class SHA1Hook(Hook):
    """Compute the SHA1 sum."""
    def __init__(self, sha1sum):
        """-sha1sum: the lowercase hex representation of the sha1 sum."""
        self._sha1sum = sha1sum
        self._hash = hashlib.sha1()

    def finish(self):
        sha1sum = self._hash.hexdigest()
        if sha1sum.lower() != self._sha1sum.lower():
            raise CorruptedFileError("sha1sum did not match: %s instead of %s"
                                     % (sha1sum, self._sha1sum))
            
    def update(self, arg):
        self._hash.update(arg)
        
    @classmethod
    def create_factory(cls, sha1sum):
        """Create a hook factory that will return SHA1Hook instances."""
        def aux():
            return cls(sha1sum)
        return aux


class ProgressBarHook(Hook):
    """Display a progress bar."""
    def __init__(self, pbar):
        self._pbar = pbar
        self._size = 0
        
    def finish(self):
        self._pbar.finish()
        
    def start(self):
        self._pbar.start()
        
    def update(self, arg):
        self._size += len(arg)
        self._pbar.update(self._size)


def new_downloaders(handlers=()):
    """Return a 2-items dictionary ret, for which:
    
    ret['default'] is a DefaultDownloader
    ret['auth'] is an AuthenticatingDownloader
    
    """
    default = DefaultDownloader(handlers)
    auth = AuthenticatingDownloader(handlers)
    return {'default': default, 'auth': auth}


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
