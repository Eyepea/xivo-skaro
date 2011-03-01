# -*- coding: UTF-8 -*-

"""HTTP service definition module.

Note that while we often talk in 'service', since we are using twisted.web
and its built around the concept of resource, a service is in fact an object
implementing twisted.web.resource.IResource.

"""

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

from twisted.internet import defer
from twisted.web import http
from twisted.web import resource
from twisted.web import static


IHTTPService = resource.IResource
"""An HTTP service is exactly the same thing as an IResource.""" 


class BaseHTTPHookService(resource.Resource):
    """Base class for HTTPHookService. Not made to be instantiated directly."""
    
    def __init__(self, service):
        resource.Resource.__init__(self)
        self._service = service

    def _next_service(self, path, request):
        # should be called in getChild method
        resrc = self._service
        if resrc.isLeaf:
            request.postpath.insert(0, request.prepath.pop())
            return resrc
        else:
            return resrc.getChildWithDefault(path, request)


class HTTPHookService(BaseHTTPHookService):
    """Base class for synchronous non-terminal service."""
    
    def _pre_handle(self, path, request):
        """This SHOULD be overridden in derived classes."""
        pass
    
    def getChild(self, path, request):
        self._pre_handle(path, request)
        return self._next_service(path, request)


class HTTPAsyncHookService(BaseHTTPHookService):
    """Base class for asynchronous non-terminal service.
    
    This is useful if you have a hook service that modify the state of the
    application but needs to wait for a callback to fire before the service
    chain can continue, because other services below this hook depends on some
    yet to come side effect.
    
    The callback is only used for flow control -- it should fire with a None
    value, since this value is going to be ignored. 
    
    IT CAN ONLY BE USED WITH A NON STANDARD IMPLEMENTATION OF SITE (see
    provd.servers.http_site.Site).
    
    """

    def _pre_handle(self, path, request):
        """This SHOULD be overridden in derived classes and must return a
        deferred that will eventually fire.
        
        """
        return defer.succeed(None)

    def getChild(self, path, request):
        d = self._pre_handle(path, request)
        d.addCallback(lambda _: self._next_service(path, request))
        return d


class HTTPLogService(HTTPHookService):
    """A small hook service that permits logging of the request."""
    def __init__(self, logger, service):
        """
        logger -- a callable object taking a string as argument
        
        """
        HTTPHookService.__init__(self, service)
        self._logger = logger
    
    def _pre_handle(self, path, request):
        # XXX this is just an example
        self._logger(str(path) + ' ---- ' + str(request))


class HTTPNoListingFileService(static.File):
    """Similar to twisted.web.static.File except that instead of listing the
    content of directories, it returns a 403 Forbidden.
    
    """
    def directoryListing(self):
        return resource.ErrorPage(http.FORBIDDEN, 'Forbidden',
                                  'Directory listing not permitted.')


if __name__ == '__main__':
    from provd.servers.http_site import Site
    from twisted.python import log
    import sys
    log.startLogging(sys.stderr)
    
    def metaaff(prefix):
        def aff(msg):
            print >>sys.stderr, prefix, msg
        return aff
    hook = HTTPLogService(metaaff('1:'), HTTPLogService(metaaff('2:'), resource.NoResource('Not found')))
    res = HTTPNoListingFileService('/home/etienne', 'application/octet-stream')
    site = Site(res)
    
    from twisted.internet import reactor
    reactor.listenTCP(8080, site)
    reactor.run()
