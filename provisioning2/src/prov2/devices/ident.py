# -*- coding: UTF-8 -*-

"""Identification, plugin association and routing services."""

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

from prov2.util import to_ip
from prov2.servers.http import HTTPHookService
from prov2.servers.tftp.service import TFTPHookService
from prov2.servers.tftp.packet import ERR_FNF
from twisted.web.resource import Resource, NoResource


# XXX should we put 'extract_device_info' and 'retrive_device' in
# classes such that its more homogenous with the other stuff ?
# TODO fix/complete the behavior of IdentificationService (lets not forget
# that its primary role is to add/modify devices from device managers)


def tftp_ip_extractor(request):
    """Return IP address (4-bytes string) from TFTP request (prov2.servers.tftp).""" 
    return request['address'][0]


def http_ip_extractor(request):
    """Return IP address (4-bytes string) from HTTP request (twisted.web)."""
    return to_ip(request.getClientIP())


# FIXME this or just defining a function ??
class DeviceInfoExtractor(object):
    """Interface."""
    def extract(self, request):
        pass


def extract_device_info(self, request):
    """Function interface.
    
    Return a device info object (less the 'ip' item since its always trivial to
    extract it) from a request or return an object that evaluates to false in
    a boolean context if it was not possible to extract information.
    
    XXX return a deferred that will callback with a device info object ?
    
    """
    raise NotImplementedError()


class ISCDHCPDeviceInfoExtractor(object):
    """Extract the MAC address from a request by querying an ISC DHCP server
    via the OMAPI protocol.
    
    """
    
    def __init__(self, ip_extractor):
        """
        ip_extractor -- a function returning the IP address from a request
        
        """
        # TODO get connection info, etc
        self._ip_extractor = ip_extractor
    
    def _retrieve_mac_from_ip(self, ip):
            # TODO extract IP, ask an ISC DHCP server via OMAPI for the lease
            # with this IP, and then extract the MAC address of this (see pypureomapi)
            raise NotImplementedError()
        
    def extract_info(self, request):
        """Provides the 'extract_device_info' function when bound to an instance."""
        ip = self._ip_extractor(request)
        try:
            mac = self._retrieve_mac_from_ip(ip)
        except Exception:
            return None
        else:
            return {'mac': mac}


class ARPDeviceInfoExtractor(object):
    """Extract the MAC address from a request by looking at the MAC address
    in the ARP table.
    
    """
    def __init__(self, ip_extractor):
        # TODO setup a netlink socket, etc
        self._ip_extractor = ip_extractor
    
    def extract_info(self, request):
        raise NotImplementedError()


class FirstCompositeDeviceInfoExtractor(object):
    """Composite device info extractor that takes a list of device info
    extractors, and return the device info object of the first extractor that
    returned a device info object.
    
    """
    def __init__(self):
        self.extractors = []
        
    def extract_info(self, request):
        """Provides the 'extract_device_info' function when bound to an instance."""
        for extractor in self.extractors:
            res = extractor(request)
            if res:
                return res
        return None


class MostPreciseCompositeDeviceInfoExtractor(object):
    """Composite device info extractor that return the device info object which
    has the more information.
    
    """
    def __init__(self):
        self.extractors = []
        
    def extract_info(self, request):
        """Provides the 'extract_device_info' function when bound to an instance."""
        res, length = None, 0
        for extractor in self.extractors:
            cur_res = extractor(request)
            if cur_res and len(cur_res) > length:
                res, length = cur_res, len(cur_res)
        return res


class CollaboratingCompositeDeviceInfoExtractor(object):
    """Composite device info extractor that return a device info object which is the
    union of the device info objects returned.
    
    """
    # TODO add conflict resolution behaviour
    def __init__(self):
        self.extractors = []
        
    def extract_info(self, request):
        """Provides the 'extract_device_info' function when bound to an instance."""
        res = {}
        for extractor in self.extractors:
            cur_res = extractor(request)
            if cur_res:
                res.update(cur_res)
        return res


def retrieve_device(dev_info, dev_mgr):
    """Function interface.
    
    Return a device object from a device manager and a device info
    object or return an object that evaluates to false in
    a boolean context if it can't find such object.
    
    """
    raise NotImplementedError()


def retrieve_device_from_ip(dev_info, dev_mgr):
    if 'ip' in dev_info:
        try:
            return dev_mgr.get_by_ip(dev_info['ip'])
        except KeyError:
            return None
    return None


def retrieve_device_from_mac(dev_info, dev_mgr):
    if 'mac' in dev_info:
        try:
            return dev_mgr.get_by_mac(dev_info['mac'])
        except KeyError:
            return None
    return None


class FallbackCompositeDeviceRetriever(object):
    def __init__(self):
        self.retrievers = []
    
    def retrieve_device(self, dev_info, dev_mgr):
        """Provides the 'retrieve_device' function when bound to an instance."""
        for retriever in self.retrievers:
            dev = retriever(dev_info, dev_mgr)
            if dev:
                return dev
        return None
    
    @classmethod
    def new_mac_then_ip_retriever(cls):
        res = cls()
        res.retrievers.append(retrieve_device_from_mac)
        res.retrievers.append(retrieve_device_from_ip)
        return res


class IdentificationService(object):
    """A generic device identification service.
    
    This extract information from requests and then potentially create or
    update devices in a device manager object with the information retrieved.
    
    XXX we could see this as a 'mangle' service; takes a request, extract info,
    then modify the state of the device manager
    
    """
    
    # TODO completer le comportement
    auto_create_no_dev_info = False
    auto_create_no_dev_info_replace = False
    auto_create = False
    auto_create_replace = False
    auto_update = False
    
    def __init__(self, dev_info_extractor, dev_retriever, dev_mgr, ip_extractor, pg_associator):
        """
        dev_info_extractor -- an 'extract_device_info' function
        dev_retriever -- an 'retrieve_device' function
        dev_mgr -- a device manager object
        ip_extractor -- a function returning the IP address from a request
        
        """
        self._dev_info_extractor = dev_info_extractor
        self._dev_retriever = dev_retriever
        self._dev_mgr = dev_mgr
        self._ip_extractor = ip_extractor
        self._pg_associator = pg_associator
    
    def identify(self, request):
        # FIXME semantic issue
        # extract device information from request (mac, mac?/vendor?/model?/version?)
        dev = None
        dev_info = self._dev_info_extractor(request)
        ip = self._ip_extractor(request)
        if not dev_info:
            # not device information could be extracted from the request. That
            # doesn't mean the device who made the request to us has never
            # been identified but it limits what we can do...
            # TODO what are we doing here ?
            # create a new device object with only an IP address ?
            # And if we create a new device, what should we do if there's
            # already a device with this IP in dev_manager ?
            dev = dev_info = {'ip': ip}
            if (self.auto_create_no_dev_info and
                not self._dev_mgr.contains_ip(ip)):
                self._dev_mgr.add_device(dev_info)
        else:
            dev_info['ip'] = ip
            # retrieve a device from the device information
            dev = self._dev_retriever(dev_info, self._dev_mgr)
            if not dev:
                # TODO what are we doing here ? create device ?
                if self.auto_create:
                    dev = dev_info
                    self._dev_mgr.add_device(dev)
            else:
                # TODO what are we doing here ? should we update the
                # device ? leave this as is ?
                if self.auto_update:
                    pass
                
        # do plugin association
        if dev and dev_info and not dev.get('plugin'):
            dev['plugin'] = self._pg_associator(dev_info)


class HTTPIdentificationService(HTTPHookService):
    """An HTTP hook service that does device identification."""
    
    def __init__(self, ident_service, service):
        """
        ident_service -- an identification service
        service -- the next HTTP service in the chain
        
        """
        HTTPHookService.__init__(self, service)
        self._ident_service = ident_service
    
    def _pre_handle(self, path, request):
        self._ident_service.identify(request)


class TFTPIdentificationService(TFTPHookService):
    """A TFTP hook service that does device identification."""
    
    def __init__(self, ident_service, service):
        """
        ident_service -- an identification service
        service -- the next TFTP service in the chain
        
        """
        TFTPHookService.__init__(self, service)
        self._ident_service = ident_service
    
    def _pre_handle(self, request):
        self._ident_service.identify(request)


def associate_to_plugin(dev_info):
    """Function interface.
    
    Takes a device info object and return a plugin name to associate to
    this device or an object that evaluates to false in a boolean context if
    it has no suggestion.
    
    """
    return NotImplementedError()


class StaticPluginAssociator(object):
    """Associate every device info to the same plugin."""
    def __init__(self, pg_name):
        self.pg_name = pg_name
    
    def associate(self, dev_info):
        """Provides the 'associate_to_plugin' function when bound to an instance."""
        return self.pg_name


class StandardMappingPluginAssociator(object):
    """Associate a device info to the plugin that says that support this type
    of device. This must be an exact match.
    
    """
    def __init__(self):
        # mapping is a mapping object where keys are (vendor, model, version) tuple and
        # values are plugin name
        self._mapping = {}
    
    def add_plugin(self, plugin):
        for device_type in plugin.device_types():
            self._mapping[device_type] = plugin.name
    
    def associate(self, dev_info):
        """Provides the 'associate_to_plugin' function when bound to an instance."""
        key = tuple(dev_info.get(k) for k in ['vendor', 'model', 'version'])
        return self._mapping.get(key)


class FirstCompositePluginAssociator(object):
    def __init__(self):
        self.associators = []
    
    def associate(self, dev_info):
        """Provides the 'associate_to_plugin' function when bound to an instance."""
        for associator in self.associators:
            res = associator(dev_info)
            if res:
                return res
        return None


class TFTPDeviceBasedRoutingService(object):
    """A service that does request routing to other services based on
    the information from the requesting device.
    
    - First, from the request IP address, it tries to find a device object
      from a device manager object.
    - Next, if it finds it, it tries to find the plugin the device is
      associated with.
    - Lastly, it routes the request to the TFTP service of the plugin.
    
    """
    def __init__(self, dev_mgr, services_map):
        # TODO define more precisely stuff related to services_map
        self._dev_mgr = dev_mgr
        self._services_map = services_map
    
    def handle_read_request(self, request, response):
        ip = tftp_ip_extractor(request)
        try:
            device = self._dev_mgr.get_by_ip(ip)
        except KeyError:
            response.reject(ERR_FNF, 'Unknown IP')
        else:
            pg_name = device.get('plugin')
            service = self._services_map.get(pg_name)
            if not service:
                self._reject('Nowhere to route this device')
            else:
                service.handle_read_request(request, response) 


class HTTPDeviceBasedRoutingService(Resource):
    """A service that does request routing to other services based on
    the information from the requesting device.
    
    - First, from the request IP address, it tries to find a device object
      from a device manager object.
    - Next, if it finds it, it tries to find the plugin the device is
      associated with.
    - Lastly, it routes the request to the HTTP service of the plugin.
    
    """
    
    def __init__(self, dev_mgr, services_map):
        Resource.__init__(self)
        self._dev_mgr = dev_mgr
        self._services_map = services_map
        
    def getChild(self, path, request):
        ip = http_ip_extractor(request)
        try:
            device = self._dev_mgr.get_by_ip(ip)
        except KeyError:
            return NoResource('Unknown IP')
        else:
            pg_name = device.get('plugin')
            service = self._services_map.get(pg_name)
            if not service:
                return NoResource('Nowhere to route this IP')
            else:
                if service.isLeaf:
                    request.postpath.insert(0, request.prepath.pop())
                    return service
                else:
                    return service.getChildWithDefault(path, request)
