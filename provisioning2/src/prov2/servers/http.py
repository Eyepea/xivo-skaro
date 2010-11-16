# -*- coding: UTF-8 -*-

"""HTTP service definition module.

Note that while we often talk in 'service', since we are using twisted.web
and its built around the concept of resource, a service is in fact an object
implementing twisted.web.resource.IResource.

"""

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

from twisted.web.resource import Resource


class HTTPHookService(Resource):
    """Base class for non-terminal service."""
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
    
    def _pre_handle(self, path, request):
        """This MAY be overridden in derived classes."""
        pass
    
    def getChild(self, path, request):
        self._pre_handle(path, request)
        resrc = self._service
        if resrc.isLeaf:
            request.postpath.insert(0, request.prepath.pop())
            return resrc
        else:
            return resrc.getChildWithDefault(path, request)


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


if __name__ == '__main__':
    from twisted.web.server import Site
    from twisted.web.resource import NoResource
    from twisted.python import log
    import sys
    log.startLogging(sys.stderr)
    
    def metaaff(prefix):
        def aff(msg):
            print >>sys.stderr, prefix, msg
        return aff
    hook = HTTPLogService(metaaff('1:'), HTTPLogService(metaaff('2:'), NoResource('Not found')))
    site = Site(hook)
    
    from twisted.internet import reactor
    reactor.listenTCP(8080, site)
    reactor.run()
