# -*- coding: UTF-8 -*-

"""This module add support to returning Deferred in Resource getChild/getChildWithDefault.
Only thing you need to do is to use this Site class instead of twisted.web.server.Site.

"""

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

import copy
import string
from twisted.internet import defer
from twisted.web import http
from twisted.web import server


class Request(server.Request):
    # originally taken from twisted.web.server.Request
    def process(self):
        "Process a request."

        # get site from channel
        self.site = self.channel.site

        # set various default headers
        self.setHeader('server', server.version)
        self.setHeader('date', http.datetimeToString())
        self.setHeader('content-type', "text/html")

        # Resource Identification
        self.prepath = []
        self.postpath = map(server.unquote, string.split(self.path[1:], '/'))
        d = self.site.getResourceFor(self)
        d.addCallback(self.render)
        d.addErrback(self.processingFailed)


class Site(server.Site):
    # originally taken from twisted.web.server.Site
    requestFactory = Request

    def getResourceFor(self, request):
        """
        Get a deferred that will callback with a resource for a request.

        This iterates through the resource heirarchy, calling
        getChildWithDefault on each resource it finds for a path element,
        stopping when it hits an element where isLeaf is true.
        """
        request.site = self
        # Sitepath is used to determine cookie names between distributed
        # servers and disconnected sites.
        request.sitepath = copy.copy(request.prepath)
        return getChildForRequest(self.resource, request)


@defer.inlineCallbacks
def getChildForRequest(resource, request):
    # originally taken from twisted.web.resource
    """
    Traverse resource tree to find who will handle the request.
    """
    while request.postpath and not resource.isLeaf:
        pathElement = request.postpath.pop(0)
        request.prepath.append(pathElement)
        retval = resource.getChildWithDefault(pathElement, request)
        if isinstance(retval, defer.Deferred):
            resource = yield retval
        else:
            resource = retval
    defer.returnValue(resource)


if __name__ == '__main__':
    from twisted.web.resource import Resource
    from twisted.web import static

    class TestResource(Resource):
        def getChild(self, path, request):
            from twisted.internet import reactor
            d = defer.Deferred()
            reactor.callLater(2, d.callback, static.Data('foobar\n', 'text/plain'))
            return d

    root = Resource()
    root.putChild('test', TestResource())
    site = Site(root)

    from twisted.internet import reactor
    reactor.listenTCP(8080, site)
    reactor.run()
    # curl -i 'http://127.0.0.1:8080/foo/bar'
