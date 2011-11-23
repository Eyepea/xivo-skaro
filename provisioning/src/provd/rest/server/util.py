# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
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

import functools
from twisted.web import http


def numeric_id_generator(prefix='', start=0):
    n = start
    while True:
        yield prefix + str(n)
        n += 1


def parse_accept(value):
    """Take the value of an Accept header and return a list of the acceptable
    mime type.
    
    """
    # Take q params into account
    tokens = [token.strip() for token in value.split(',')]
    return [token.split(';', 1)[0] for token in tokens]


def accept_mime_type(mime_type, request):
    """Return true if mime_type is an acceptable mime-mime_type for the response
    for the request.
    
    """
    if request.getHeader('Accept') is None:
        return True
    else:
        accept = parse_accept(request.getHeader('Accept'))
        if mime_type in accept or '*/*' in accept:
            return True
        elif mime_type[:mime_type.index('/')] + '/*' in accept:
            return True
        else:
            return False


def accept(mime_types):
    """Decorator to restrict the MIME type a Resource render method
    can accept, i.e. check the Accept header value.
    
    """
    def in_accept(fun):
        @functools.wraps(fun)
        def aux(self, request):
            for mime_type in mime_types:
                if accept_mime_type(mime_type, request):
                    return fun(self, request)
            else:
                request.setResponseCode(http.NOT_ACCEPTABLE)
                request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                return (u"You must accept one of the following MIME type '%s'."
                        % mime_types).encode('UTF-8')
        return aux
    return in_accept


def content_type(mime_type):
    def in_content_type(fun):
        @functools.wraps(fun)
        def aux(self, request):
            content_type = request.getHeader('Content-Type')
            if not content_type or content_type not in mime_type:
                request.setResponseCode(http.UNSUPPORTED_MEDIA_TYPE)
                request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                return (u"Entity must be in one of these media types '%s'."
                        % mime_type).encode('UTF-8')
            else:
                return fun(self,request)
        return aux
    return in_content_type

