# -*- coding: UTF-8 -*-

"""Extension to the fetchfw.download module so that it's usable in an
asynchronous application.

"""

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

from fetchfw import download
from provd.operation import OperationInProgress, OIP_SUCCESS, OIP_FAIL,\
    OIP_PROGRESS
from twisted.internet import threads, defer


def async_download(remote_file, supp_hooks=[]):
    """Download a file asynchronously.
        
    Return a deferred that will fire with None once the download is completed
    or fire its errback if the download failed.
    
    """
    return threads.deferToThread(remote_file.download, supp_hooks)


class _OperationInProgressHook(download.DownloadHook):
    def __init__(self, oip):
        self._oip = oip
        self._oip.current = 0
    
    def start(self):
        self._oip.state = OIP_PROGRESS
    
    def update(self, arg):
        self._oip.current += len(arg)


def async_download_with_oip(remote_file, supp_hooks=[]):
    """Download a file asynchronously.
    
    Return a tuple (deferred, operation in progress). The deferred will fire
    with None once the donwload is completed or fire its errback if the
    download failed.
    
    """
    oip = OperationInProgress(end=remote_file.size)
    oip_hook = _OperationInProgressHook(oip)
    deferred = async_download(remote_file, [oip_hook] + supp_hooks)
    def callback(res):
        oip.state = OIP_SUCCESS
        return res
    def errback(err):
        oip.state = OIP_FAIL
        return err
    deferred.addCallbacks(callback, errback)
    return (deferred, oip)


def async_download_multiseq_with_oip(remote_files):
    """Download multiple files asynchronously,in a sequential way.
    
    Return a tuple (deferred, operation in progress).
    
    If one download fails, the other downloads will not be started.
    
    """
    remote_files = list(remote_files)
    top_oip = OperationInProgress(state=OIP_PROGRESS)
    top_deferred = defer.Deferred()
    # can't use nonlocal statement since we are using python 2, so we
    # use a list to hold the current file index
    cur_file_idx = [-1]
    def download_next_file():
        cur_file_idx[0] += 1
        if cur_file_idx[0] < len(remote_files):
            remote_file = remote_files[cur_file_idx[0]]
            dl_deferred, dl_oip = async_download_with_oip(remote_file)
            top_oip.sub_oips.append(dl_oip)
            dl_deferred.addCallbacks(callback, errback)
        else:
            top_oip.state = OIP_SUCCESS
            top_deferred.callback(None)
    def callback(res):
        # succesful download of current file
        download_next_file()
    def errback(err):
        # failed download of current file
        top_oip.state = OIP_FAIL
        top_deferred.errback(err)
    download_next_file()
    return (top_deferred, top_oip)


if __name__ == '__main__':
    import logging
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler())
    root_logger.setLevel(logging.INFO)
    from provd.operation import format_oip
    
    from twisted.internet import reactor
    def main():
        dler = download.DefaultDownloader([])
        rfile1 = download.RemoteFile('/tmp/pytest/test-dl1',
                                     'http://localhost:8000/fich.bin',
                                     dler,
                                     100000)
        rfile2 = download.RemoteFile('/tmp/pytest/test-dl2',
                                     'http://localhost:8000/fich2.bin',
                                     dler,
                                     100000)
        abort_hook = download.AbortHook()
        #d, oip = async_download_with_oip(rfile1, [abort_hook])
        d, oip = async_download_multiseq_with_oip([rfile1, rfile2])
        def on_succes(v):
            print_oip()
            print "success", v
            reactor.stop()
        def on_failure(e):
            print_oip()
            print "fail", e
            reactor.stop()
        def print_oip():
            print format_oip(oip)
            reactor.callLater(0.5, print_oip)
        d.addCallbacks(on_succes, on_failure)
        print_oip()
#        reactor.callLater(0.5, abort_hook.abort_download)
    
    reactor.callLater(0, main)
    reactor.run()
