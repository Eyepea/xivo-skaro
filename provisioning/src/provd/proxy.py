# -*- coding: UTF-8 -*-

"""Extension to the urllib2 module that adds a proxy handler that can
be modified after its creation.

"""

__license__ = """
    Copyright (C) 2011  Avencall

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

import urllib2


class DynProxyHandler(urllib2.ProxyHandler):
    # - this targets cpython 2.6, it might not work on a different version.
    # - this only supports proxy for http, ftp and https. I did not try to
    #   find the exact reason why, but it looks like the list of '*_open'
    #   method is built at opener creation time, so it's impossible to have
    #   something truly dynamic without hacking urllib2 more

    def __init__(self, proxies):
        # do NOT call ProxyHandler.__init__. We still need to
        # inherit from it to fit in urllib2 handlers framework
        self._proxies = proxies

    def _generic_open(self, proto, req):
        if proto in self._proxies:
            try:
                proxy = self._proxies[proto]
            except KeyError:
                # just in case a race condition happens, although it should
                # not in theory
                return None
            else:
                return self.proxy_open(req, proxy, proto)
        else:
            return None

    def http_open(self, req):
        return self._generic_open('http', req)

    def ftp_open(self, req):
        return self._generic_open('ftp', req)

    def https_open(self, req):
        return self._generic_open('https', req)
