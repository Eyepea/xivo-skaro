# -*- coding: UTF-8 -*-

"""A synchronous client for the REST API of the provisioning server."""

from __future__ import with_statement

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
import functools
import urlparse
import urllib2
from urllib2 import Request, HTTPError
import simplejson as json

# Note that we are currently using URI templates instead of using the various
# hypermedia control returned by the server. This feel a lot simpler... but we
# might want to eventually consider the more robust solution...
# XXX we might want to look at using something else than urllib2... 

PROV_MIME_TYPE = 'application/vnd.proformatique.prov+json'


class RemoteServerError(Exception):
    """Raised when the server returns a 50X status code."""
    pass


class LocalClientError(Exception):
    pass


def _wrap_5xx(fun):
    @functools.wraps(fun)
    def aux(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except HTTPError, e:
            if 500 <= e.code < 600:
                raise RemoteServerError(e)
            else:
                raise
    return aux


# Extending urllib2, which is not a generic HTTP client library...
class DeleteRequest(Request):
    def get_method(self):
        return "DELETE"


class PutRequest(Request):
    def get_method(self):
        return "PUT"
    
    
class MyHTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    """Process HTTP error responses.
    
    Modified version of urllib2.HTTPErrorProcessor so that when the server
    return a 200 code, an HTTPError is not raised.
    
    """
    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        if code < 200 or code > 299:
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)

        return response

    https_response = http_response


class RestClientService(object):
    # XXX do we need to quote (urllib.quote) inputs that are used
    #     directly to build an URL ?
    # XXX list_cfg and list_dev doesn't return the same thing (one return
    #     the id + the object, the other only the ID). We might want to
    #     make this more homogenous
    # TODO refactoring, lots of similar/duplicated code
    
    ENTRY_DEV = 'devices'
    ENTRY_CFG = 'configs'
    
    def __init__(self, base_url, opener=urllib2.build_opener(MyHTTPErrorProcessor())):
        self._base_url = base_url
        self._opener = opener
        
    @_wrap_5xx
    def add_dev(self, dev):
        """Add a device to the server and return the (IDs, device) of the newly added
        device.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_DEV)
        req_content = json.dumps({'device': dev})
        request = Request(url, req_content, {'Accept': PROV_MIME_TYPE, 'Content-Type': PROV_MIME_TYPE})
        f = self._opener.open(request)
        with contextlib.closing(f):
            resp_content = json.load(f)
        dev_id = resp_content['id']
        dev = resp_content['device']
        return dev_id, dev
    
    def remove_dev(self, dev_id):
        """Remove a device and return True if the remove was sucessful, False
        if device not found.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_DEV + '/' + dev_id)
        request = DeleteRequest(url)
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return False
            else:
                raise
        f.close()
        return True
    
    def get_dev(self, dev_id):
        """Return a device object from a device ID, or None if the
        there's no device with such ID.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_DEV + '/' + dev_id)
        request = Request(url, None, {'Accept': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return None
            else:
                raise
        with contextlib.closing(f):
            content = json.load(f)
        dev = content['device']
        return dev
    
    def set_dev(self, dev_id, dev):
        """Update a device object and return true if update has been
        successful, false if no such device.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_DEV + '/' + dev_id)
        req_content = json.dumps({'device': dev})
        request = PutRequest(url, req_content, {'Content-Type': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return False
            else:
                raise
        f.close()
        return True
    
    @_wrap_5xx
    def list_dev(self):
        """Return all the devices managed by the server in the form of a
        (id, device object) tuples.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_DEV)
        request = Request(url, None, {'Accept': PROV_MIME_TYPE})
        f = self._opener.open(request)
        with contextlib.closing(f):
            content = json.load(f)
        
        try:
            for dev_entry in content['devices']:
                yield dev_entry['id'], dev_entry['device']
        except KeyError, e:
            raise LocalClientError('content format has changed', e)
    
    @_wrap_5xx
    def reconfigure_dev(self, dev_id):
        """Reconfigure a device and return true if the device has been
        reconfigured, false if there was something wrong.
        
        Note that for device like the Aastra 6731i using configuration files on a
        provisioning server, reconfiguring is only the step of regenerating the file
        on the server; you need to ask the device to reload its configuration next.
        For device like the Siemens C470IP where configuration is done directly
        via the web interface, there's no reload step, and the configuration will
        fail if the device is not up. 
        
        """
        url = urlparse.urljoin(self._base_url, 'dev_reconfigure')
        req_content = json.dumps({'id': dev_id})
        request = Request(url, req_content, {'Content-Type': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 400:
                return False
            else:
                raise
        f.close()
        return True
    
    @_wrap_5xx
    def reload_dev(self, dev_id):
        """Reload a device and return true if the device has been
        reloaded, false if there was something wrong.
        
        """
        url = urlparse.urljoin(self._base_url, 'dev_reload')
        req_content = json.dumps({'id': dev_id})
        request = Request(url, req_content, {'Content-Type': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 400:
                return False
            else:
                raise
        f.close()
        return True
    
    @_wrap_5xx
    def list_cfg(self):
        """Return all the configs IDs managed by the server."""
        url = urlparse.urljoin(self._base_url, self.ENTRY_CFG)
        request = Request(url, None, {'Accept': PROV_MIME_TYPE})
        f = self._opener.open(request)
        with contextlib.closing(f):
            content = json.load(f)
        
        for cfg_entry in content['configs']:
            yield cfg_entry['id']

    @_wrap_5xx
    def get_cfgi(self, cfg_id):
        """Return a tuple of (cfg, cfg_base_ids) for the config with ID cfg_id,
        or None if no such config exist.
        
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_CFG + '/' + cfg_id + '?f=i')
        request = Request(url, None, {'Accept': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return None
            else:
                raise
        with contextlib.closing(f):
            content = json.load(f)
        
        cfg = content['config']
        cfg_base_ids = [cfg_base_entry['id'] for cfg_base_entry in content['config-bases']]
        #cfg_base_ids = content['config-bases']
        return cfg, cfg_base_ids
    
    @_wrap_5xx
    def get_cfgc(self, cfg_id):
        url = urlparse.urljoin(self._base_url, self.ENTRY_CFG + '/' + cfg_id + '?f=c')
        request = Request(url, None, {'Accept': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return None
            else:
                raise
        with contextlib.closing(f):
            content = json.load(f)
        
        cfg = content['config']
        return cfg 

    @_wrap_5xx
    def remove_cfg(self, cfg_id):
        url = urlparse.urljoin(self._base_url, self.ENTRY_CFG + '/' + cfg_id)
        request = DeleteRequest(url)
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return False
            else:
                raise
        f.close()
        return True
    
    @_wrap_5xx
    def set_cfg(self, cfg_id, cfg, cfg_base_ids):
        """Update/add a config and return true if it has been
        successful, else false.
        
        cfg_base_ids is a list of config IDs
        """
        url = urlparse.urljoin(self._base_url, self.ENTRY_CFG + '/' + cfg_id)
        config_bases = [{'id': cfg_base_id} for cfg_base_id in cfg_base_ids]
        req_content = json.dumps({'config': cfg, 'config-bases': config_bases})
        request = PutRequest(url, req_content, {'Content-Type': PROV_MIME_TYPE})
        try:
            f = self._opener.open(request)
        except HTTPError, e:
            if e.code == 404:
                return False
            else:
                raise
        f.close()
        return True


