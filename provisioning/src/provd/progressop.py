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

import urlparse
from twisted.internet import defer
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import ClientCreator, Protocol
from twisted.protocols.ftp import FTPClient
from twisted.web.client import Agent, ResponseDone


def request(url, fobj):
    if url.startswith('http://'):
        return HTTPDownloadFactory().request(url, fobj)
    elif url.startswith('ftp://'):
        return FTPDownloadFactory().request(url, fobj)
    else:
        raise ValueError("unsupported URL '%s'" % url)


class HTTPDownloadFactory(object):
    def __init__(self, agent=None):
        if agent is None:
            from twisted.internet import reactor
            self.agent = Agent(reactor)
        else:
            self.agent = agent
    
    def request(self, url, fobj):
        """Return an object providing IOperationInProgress...
        
        url must be an URL beginning with 'http://'.
        
        Note: fobj will NOT be closed after the download.
        
        """
        return _HTTPDownloadOperation(url, fobj, self.agent)


class _HTTPDownloadOperation(object):
    #implements(IOperationInProgress)
    
    # TODO take username/password/realm into account
    
    def __init__(self, url, fobj, agent):
        self._fobj = fobj
        self.deferred = defer.Deferred()
        self.status = "progress"
        
        d = agent.request('GET', url)
        d.addCallbacks(self._process_body, self._on_agent_error)

    def _on_agent_error(self, failure):
        self.status = "fail"
        self.deferred.errback(failure)
        
    def _process_body(self, response):
        # TODO handle 401 and 3xx status code
        if response.code != 200:
            self.deferred.errback(ValueError("Received status code %s"
                                             % response.code))
            self.status = "fail"
            response.deliverBody(_DiscardContent())
        else:
            response.deliverBody(_WriteContent(self, response.length))


class _WriteContent(Protocol):
    def __init__(self, op, length=None):
        self._op = op
        if length is None:
            self.dataReceived = self._dataReceived 
        else:
            self.dataReceived = self._dataReceived_ext
            self._cur_length = 0
            self._length = length
            self._set_status()
    
    def _set_status(self):
        self._op.status = "progress;%d/%d" % (self._cur_length, self._length)
        #print self._op.status
    
    def _dataReceived(self, bytes):
        self._op._fobj.write(bytes)

    def _dataReceived_ext(self, bytes):
        # XXX if _fobj.write fail, we should do something...
        self._op._fobj.write(bytes)
        self._cur_length += len(bytes)
        self._set_status()

    def connectionLost(self, reason):
        #print reason.type
        if isinstance(reason.value, ResponseDone) or \
           isinstance(reason.value, ConnectionDone):
            self._op.status = "success"
            self._op.deferred.callback(None)
        else:
            self._op.status = "fail"
            self._op.deferred.errback(reason)


class _DiscardContent(Protocol):
    def connectionMade(self):
        self.transport.stopProducing()


class FTPDownloadFactory(object):
    def __init__(self, reactor=None):
        if reactor is None:
            from twisted.internet import reactor
            self.reactor = reactor
        else:
            self.reactor = reactor
    
    def request(self, url, fobj):
        """Return an object providing IOperationInProgress...
        
        url must be an URL beginning with 'ftp://'.
        
        Note: fobj will NOT be closed after the download.
        
        """
        return _FTPDownloadOperation(url, fobj, self.reactor)


class _FTPDownloadOperation(object):
    #implements(IOperationInProgress)
    
    # TODO take username/password into account
    
    def __init__(self, url, fobj, reactor):
        self._purl = purl = urlparse.urlparse(url)
        if purl.scheme != 'ftp' or not purl.hostname:
            raise ValueError('invalid url')
        
        self._fobj = fobj
        self.deferred = defer.Deferred()
        self.status = "progress"
        
        creator = ClientCreator(reactor, FTPClient)
        d = creator.connectTCP(purl.hostname, purl.port or 21)
        d.addCallbacks(self._continue, self._on_error)
    
    def _on_error(self, failure):
        self.status = "fail"
        self.deferred.errback(failure)
        
    def _continue(self, ftp_client):
        d = ftp_client.retrieveFile(self._purl.path, _WriteContent(self))
        d.addBoth(lambda x: ftp_client.quit().addBoth(lambda x: None))


if __name__ == '__main__':
    import StringIO
    from twisted.python.util import println
    
    #fobj = StringIO.StringIO()
    fobj = open('/tmp/dl.bin', 'wb')
    
    #dler = HTTPDownloadFactory().request('http://downloads.digium.com/pub/telephony/firmware/releases/dahdi-fw-oct6114-064-1.05.01.tar.gz', fobj)
    dler = FTPDownloadFactory().request('ftp://ftp.sangoma.com/firmware/A101dm_0040_V36.BIN', fobj)
    dler.deferred.addBoth(lambda x: println(dler.status))
#    dler.deferred.addCallback(lambda x: println(fobj.getvalue()))
#    dler.deferred.addErrback(lambda x: println(x))
    dler.deferred.addBoth(lambda x: fobj.close())
    
    from twisted.internet import reactor
    reactor.callLater(5, reactor.stop)
    reactor.run()
