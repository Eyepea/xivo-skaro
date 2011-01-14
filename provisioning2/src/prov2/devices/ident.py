# -*- coding: UTF-8 -*-

"""Request processing service definition."""

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

import logging
from prov2.plugins import BasePluginManagerObserver
from prov2.servers.tftp.service import TFTPNullService
from twisted.internet import defer
from twisted.web.resource import Resource, NoResource
from zope.interface import Interface, implements

logger = logging.getLogger('ident')

# TODO handle the case where ProcessingService.process return a Deferred
#      that fires it's errback. In TFTP and HTTP request processing service.
# XXX althought the possibility of returning a deferred in a device info
#     extractor means more flexibility, it adds complexity (but then,
#     that's not too bad) but also mean that if we log, we could have
#     interleaved logging from different request in theory (actually
#     since we are not using this deferred possibility, this does not
#     apply). 

def _extract_tftp_ip(request):
    """Utility function that return the IP address from a TFTP request
    object (prov2.servers.tftp).
    
    """ 
    return request['address'][0]


def _extract_http_ip(request):
    """Utility function that return the IP address from an HTTP request
    object (twisted.web).
    
    """
    return request.getClientIP()


def _extract_ip(request, request_type):
    if request_type == 'http':
        return _extract_http_ip(request)
    elif request_type == 'tftp':
        return _extract_tftp_ip(request)
    else:
        return None


class IDeviceInfoExtractor(Interface):
    """A device info extractor object extract device information from
    requests. In our context, requests are either HTTP, TFTP or DHCP
    requests.
    
    Example of information that can be extracted are:
    - MAC address
    - vendor name
    - model name
    - version number
    - serial number
    
    Note: DHCP requests are not processed by the provisioning server per se.
    The way it works is that DHCP requests can be made available to the
    provisioning server, which can then used them to help with the extraction
    of information for TFTP or HTTP requests.
    
    For example, since it's always possible to extract the IP of a TFTP/HTTP
    requests, the provisioning server could then look if it has information on
    a DHCP requests with this IP address. If it does, it could then extract
    information from that DHCP requests, and return this information in the
    device information object that will be returned in the TFTP/HTTP extract
    operation.
    
    This way, for example, you can always extract the MAC address of TFTP
    requests even if there's no such information in the TFTP request
    directly.
    
    """
    
    def extract(request, request_type):
        """Return a Deferred that will callback with either an non empty
        device info object or an object that evaluates to false in a boolean
        context if no information could be extracted.
        
        Note that the IP address MUST NOT be returned in the device info
        object.
        
        So far, request_type is either 'http', 'tftp' or 'dhcp'.
        - For 'http', request is a twisted.web.http.Request object.
        - For 'tftp', request is a prov2.servers.tftp.request object.
        - For 'dhcp', request is a dictionary object with keys 'mac' and
          'dhcp_opts'.
        
        """


class StaticDeviceInfoExtractor(object):
    """Device info extractor that always return the same device information.
    
    Note: can be used as a 'NullDeviceInfoExtractor' if 'self.dev_info is None'.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, dev_info=None):
        self.dev_info = dev_info

    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        return defer.succeed(self.dev_info)

    
class DHCPDeviceInfoExtractor(object):
    """Device info extractor that return the MAC address and other
    information from requests with the help of external DHCP information.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, dhcp_infos, dhcp_xtor):
        """
        dhcp_info_src -- a mapping object where keys are IP address and values are
          mapping object with the 'mac' and 'dhcp_opts' keys, where the value of
          'mac' is a MAC address (in normalized format) and the value of 'dhcp_opts'
          is another mapping object where keys are integer representing the code of
          a DHCP option and value are the raw option value as a string
        dhcp_xtor -- a device info extractor that accept DHCP info object and a
          request type of 'dhcp' and return a device info object (without the
          MAC address).
        """
        self._dhcp_infos = dhcp_infos
        self._dhcp_xtor = dhcp_xtor
    
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        ip = _extract_ip(request, request_type)
        if ip not in self._dhcp_infos:
            return defer.succeed(None)
        else:
            dhcp_info = self._dhcp_infos[ip]
            dev_info = self._dhcp_xtor.extract(dhcp_info, 'dhcp')
            if not dev_info:
                dev_info = {}
            dev_info['mac'] = dhcp_info['mac']
            return defer.succeed(dev_info)


class ArpDeviceInfoExtractor(object):
    """Device info extractor that return the MAC address from requests by
    looking up the ARP table.
    
    Note that this extractor is only useful if the request is on the same
    broadcast domain as the machine.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, extract_ip):
        # TODO setup a netlink socket, etc
        self._extract_ip = extract_ip
    
    def extract(self, request, request_type):
        return defer.fail(NotImplementedError())


# XXX huh ? As far as I can see, this is useless and might be deleted
class TypeBasedDeviceInfoExtractor(object):
    """A device info extractor that ask another device info extractor
    depending on the request type of the request.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, extractor_map=None):
        self.extractor_map = {} if extractor_map is None else extractor_map
    
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        if request_type in self.extractor_map:
            return self.extractor_map[request_type].extract(request, request_type)
        else:
            return defer.succeed(None)


class CompositeDeviceInfoExtractor(object):
    """Abstract base class for device info extractor that return a result
    based on zero or more underlying device info extractors. Not made to
    be instantiated.
    
    """
    
    def __init__(self, extractors=None):
        self.extractors = [] if extractors is None else extractors


class FirstCompositeDeviceInfoExtractor(CompositeDeviceInfoExtractor):
    """Composite device info extractor that return the device info object of
    the first extractor that returned a nonempty device info object.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    @defer.inlineCallbacks
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        extractors = self.extractors[:]
        for extractor in extractors:
            dev_info = yield extractor.extract(request, request_type)
            if dev_info:
                defer.returnValue(dev_info)
        defer.returnValue(None)


class LongestDeviceInfoExtractor(CompositeDeviceInfoExtractor):
    """Composite device info extractor that return the device info object
    with the most items.
    
    In the case where at least two extractors return a device info object
    of the same length, the result of the first extractor will be returned.
    
    """
    
    implements(IDeviceInfoExtractor)
        
    @defer.inlineCallbacks
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        dlist = defer.DeferredList([extractor.extract(request, request_type)
                                    for extractor in self.extractors],
                                    consumeErrors=True)
        dev_infos = yield dlist
        dev_info, length = None, 0
        for success, cur_dev_info in dev_infos:
            if success and cur_dev_info and len(cur_dev_info) > length:
                dev_info, length = cur_dev_info, len(cur_dev_info)
        defer.returnValue(dev_info)


def _find_key_conflicts(base, new):
    """Split the new dictionary into a conflicts and nonconflicts
    dictionaries, such that:
    - for key in conflicts: key in base
    - for key in nonconflicts: key not in base
    - conflicts.update(nonconflicts) == new
    - nonconflicts.update(conflicts) == new
    
    """
    conflicts, nonconflicts = {}, {}
    for k, v in new.iteritems():
        if k in base:
            conflicts[k] = v
        else:
            nonconflicts[k] = v
    return conflicts, nonconflicts


class FirstSeenUpdater(object):
    """Updater for CollaboratingDeviceInfoExtractor that, on conflict, keep
    the first seen value.
    
    """
    def __init__(self):
        self.dev_info = {}
    
    def update(self, dev_info):
        nonconflicts = _find_key_conflicts(self.dev_info, dev_info)[1]
        self.dev_info.update(nonconflicts)


class LastSeenUpdater(object):
    """Updater for CollaboratingDeviceInfoExtractor that, on conflict, keep
    the last seen value.
    
    """
    def __init__(self):
        self.dev_info = {}
    
    def update(self, dev_info):
        self.dev_info.update(dev_info)


class RemoveUpdater(object):
    """Updater for CollaboratingDeviceInfoExtractor that will return a device
    info object with only keys that are not in conflict.
    
    """
    
    def __init__(self):
        self.dev_info = {}
        self._conflicts = set()
        
    def update(self, dev_info):
        conflicts, nonconflicts = _find_key_conflicts(self.dev_info, dev_info)
        for k, v in nonconflicts.iteritems():
            if k not in self._conflicts:
                self.dev_info[k] = v
        for k in conflicts:
            del self.dev_info[k]
            self._conflicts.add(k)


class VotingUpdater(object):
    """Updater for CollaboratingDeviceInfoExtractor that will return a device
    info object such that values are the most popular one.
    
    Note that in the case of a tie, it returns any of the most popular values.
    
    """
    
    def __init__(self):
        self._votes = {}
    
    def _vote(self, (key, value)):
        key_pool = self._votes.setdefault(key, {})
        key_pool[value] = key_pool.get(value, 0) + 1
    
    def _get_winner(self, key_pool):
        # Pre: key_pool is non-empty
        # XXX we are not doing any conflict resolution if key_pool has
        #     a tie. What's worst is that it's not totally deterministic.
        return max(key_pool.iteritems(), key=lambda x: x[1])[0]
    
    @property
    def dev_info(self):
        dev_info = {}
        for key, key_pool in self._votes.iteritems():
            dev_info[key] = self._get_winner(key_pool)
        return dev_info
    
    def update(self, dev_info):
        for item in dev_info.iteritems():
            self._vote(item)


class CollaboratingDeviceInfoExtractor(CompositeDeviceInfoExtractor):
    """Composite device info extractor that return a device info object
    which is the composition of every device info objects returned.

    Takes an Updater factory to control the way the returned device info
    object is builded.
    
    An Updater is an object with an:
    - 'update' method, taking a dev_info object and returning nothing
    - 'dev_info' attribute, which is the current computed dev_info
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, updater_factory, extractors=None):
        CompositeDeviceInfoExtractor.__init__(self, extractors)
        self._updater_factory = updater_factory
    
    @defer.inlineCallbacks
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        dlist = defer.DeferredList([extractor.extract(request, request_type)
                                    for extractor in self.extractors],
                                    consumeErrors=True)
        dev_infos = yield dlist
        updater = self._updater_factory()
        for success, dev_info in dev_infos:
            if success and dev_info:
                updater.update(dev_info)
        defer.returnValue(updater.dev_info)


class PluginDeviceInfoExtractor(object):
    """Device info extractor that forward extraction requests to the
    device info extractors of a plugin, if the plugin is loaded.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, pg_id, pg_mgr):
        self._pg_id = pg_id
        self._pg_mgr = pg_mgr
        self._set_pg()
        # observe plugin loading/unloading
        obs = BasePluginManagerObserver(self._set_pg, self._set_pg)
        pg_mgr.attach(obs)
    
    def _set_pg(self, *args):
        if self._pg_id in self._pg_mgr:
            self._pg = self._pg_mgr[self._pg_id]
        else:
            self._pg = None
    
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        if self._pg is None:
            return defer.succeed(None)
        else:
            xtor = getattr(self._pg, request_type + '_dev_info_extractor')
            return xtor.extract(request, request_type)


class AllPluginsDeviceInfoExtractor(object):
    """Composite device info extractor that forward extraction requests to
    device info extractors of every loaded plugins.
    
    """
    
    implements(IDeviceInfoExtractor)
    
    def __init__(self, extractor_factory, pg_mgr):
        """
        extractor_factory -- a function taking a list of extractors and
          returning an extractor.
        """
        self.extractor_factory = extractor_factory
        self._pg_mgr = pg_mgr
        self._set_xtors()
        # observe plugin loading/unloading
        obs = BasePluginManagerObserver(self._set_xtors, self._set_xtors)
        pg_mgr.attach(obs)
    
    def _xtor_name(self, request_type):
        return '_%s_xtor' % request_type
    
    def _set_xtors(self):
        for request_type in ('http', 'tftp', 'dhcp'):
            pg_extractors = []
            for pg in self._pg_mgr.itervalues():
                pg_extractor = getattr(pg, request_type + '_dev_info_extractor')
                if pg_extractor is not None:
                    pg_extractors.append(pg_extractor)
            xtor = self.extractor_factory(pg_extractors)
            setattr(self, self._xtor_name(request_type), xtor)
    
    def extract(self, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        xtor = getattr(self, self._xtor_name(request_type))
        return xtor.extract(request, request_type)


# do we want to receive an app object or should object store it locally ?
class IDeviceRetriever(Interface):
    """A device retriever return a device object from device information.
    
    Instances providing this interface MAY have some side effect on the
    application, like adding a new device.
    
    """
    
    def retrieve(dev_info, app):
        """Return a device object from a device info object or None if it can't
        find such object.
        
        dev_info has ALWAYS the key 'ip' set to the IP address of the device.
        That means dev_info is always 'true' and dev_info['ip'] never raise
        a KeyError.
        
        """


class NullDeviceRetriever(object):
    """Device retriever who never retrieves anything."""
    implements(IDeviceRetriever)
    
    def retrieve(self, dev_info, app):
        logger.debug('In %s', self.__class__.__name__)
        return None


class IpDeviceRetriever(object):
    """Retrieve device object by looking up in a device manager for an
    object which IP is the same as the device info object.
    
    """
    implements(IDeviceRetriever)
    
    def retrieve(self, dev_info, app):
        logger.debug('In %s', self.__class__.__name__)
        dev_mgr = app.dev_mgr
        dev_id = dev_mgr.find_ip(dev_info['ip'])
        if dev_id is not None:
            return dev_mgr[dev_id]
        return None


class MacDeviceRetriever(object):
    """Retrieve device object by looking up in a device manager for an
    object which MAC is the same as the device info object.
    
    """
    implements(IDeviceRetriever)
    
    def retrieve(self, dev_info, app):
        logger.debug('In %s', self.__class__.__name__)
        dev_mgr = app.dev_mgr
        if 'mac' in dev_info:
            dev_id = dev_mgr.find_mac(dev_info['mac']) 
            if dev_id is not None:
                return dev_mgr[dev_id] 
        return None


class SerialNumberDeviceRetriever(object):
    """Retrieve device object by looking up in a device manager for an
    object which serial number is the same as the device info object.
    
    """
    implements(IDeviceRetriever)
    
    def retrieve(self, dev_info, app):
        logger.debug('In %s', self.__class__.__name__)
        dev_mgr = app.dev_mgr
        if 'sn' in dev_info:
            serial_number = dev_info['sn']
            def _find_fun(dev):
                if dev.get('sn') == serial_number:
                    return True
                return False
            dev_id = dev_mgr.find(_find_fun) 
            if dev_id is not None:
                return dev_mgr[dev_id] 
        return None


class AddDeviceRetriver(object):
    """A device retriever that does no lookup and always add a new device
    object to the device manager.
    
    Mostly useful if used in a FirstCompositeDeviceRetriever at the end of
    the list, in a way that it will be called only if the other retrievers
    don't find anything.
    
    """
    implements(IDeviceRetriever)
    
    def retrieve(self, dev_info, app):
        logger.debug('In %s', self.__class__.__name__)
        dev = dict(dev_info)
        app.create_dev(dev)
        return dev


class FirstCompositeDeviceRetriever(object):
    """Composite device retriever which return the device its first retriever
    returns.
    
    """
    
    def __init__(self, retrievers=None):
        self.retrievers = [] if retrievers is None else retrievers
    
    def retrieve(self, dev_info, dev_mgr):
        logger.debug('In %s', self.__class__.__name__)
        for retriever in self.retrievers:
            dev = retriever.retrieve(dev_info, dev_mgr)
            if dev is not None:
                return dev
        return None


class IDeviceUpdater(Interface):
    """Update a device object device from an info object.
    
    This operation can have side effect, like updating the device. In fact,
    being able to do side effects is why this interface exist.
    
    Also, you should refrain from doing stupid thing, like removing the
    'ip' key, or modifying the 'config' value without returning true. This
    break this interface contract, and will yield to exception, incorrect
    behaviours elsewhere in the application.  
    
    """
    
    def update(dev, dev_info, request, request_type):
        """Update a device object with a device info object. Return true
        if the device has been updated and should probably be reconfigured,
        false if it has not.
        
        # XXX should specify the return value more clearly
        
        dev -- a nonempty device object
        dev_info -- a nonempty device info object for which the key 'ip' is
          always present
        
        Pre: dev_info['ip'] doesn't raise KeyError
        
        """


class NullDeviceUpdater(object):
    """Device updater that updates nothing."""
    
    implements(IDeviceUpdater)
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        return False


class StaticDeviceUpdater(object):
    """Static device updater that update a key-value pair of the device.
    
    If the key is already present in the device, the force_update attribute
    determine the behavior; if true, this key will be updated, else it
    won't.
    
    """
    
    implements(IDeviceUpdater)
    
    force_update = False
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        if self.force_update or self.key not in dev:
            old_value = dev.get(self.key)
            if old_value != self.value:
                dev[self.key] = self.value
                return True
        return False


class AddInfoDeviceUpdater(object):
    """Device updater that add any missing information to the device from
    the device info.
    
    """
    
    implements(IDeviceUpdater)
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        updated = False
        for key in dev_info:
            if key not in dev:
                dev[key] = dev_info[key]
                updated = True
        return updated


class EverythingDeviceUpdater(object):
    """Device updater that updates everything.
    
    XXX This is wild.
    
    """
    
    implements(IDeviceUpdater)
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        # XXX the specification for device object in the device module
        #     doesn't tell that device object must have a clear and update
        #     method... so we might want to change the specification so
        #     this kind of code is correct and 'standard'...
        dev.clear()
        dev.update(dev_info)
        return True     # in fact, its possible that dev_info didn't change


class IpDeviceUpdater(object):
    """Device updater that updates the IP address."""
    
    implements(IDeviceUpdater)
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        if dev['ip'] != dev_info['ip']:
            dev['ip'] = dev_info['ip']
            return True
        return False


class VersionDeviceUpdater(object):
    """If 'model' in dev and 'version' in dev_info, then update dev['version']
    to dev_info['version'].
    
    """ 
    
    implements(IDeviceUpdater)
    
    delete_on_no_version = True
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        updated = False
        if 'vendor' in dev and 'model' in dev:
            if 'version' in dev_info:
                dev['version'] = 'version'
                updated = True
            else:
                if self.delete_on_no_version and 'version' in dev:
                    del dev['version']
                    updated = True
        return updated


class LoggingDeviceUpdater(object):
    """Doesn't update anything but log a message if there's a difference
    between the device and the device info objects.
    
    """
    
    implements(IDeviceUpdater)
    
    def update(self, dev, dev_info, request, request_type):
        # TODO specify the behavior and implement it, if useful
        return False


class CompositeDeviceUpdater(object):
    implements(IDeviceUpdater)
    
    def __init__(self, updaters=None):
        self.updaters = [] if updaters is None else updaters
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        updated = False
        for updater in self.updaters:
            updated = updater.update(dev, dev_info, request, request_type) or updated
        return updated


class IDeviceRouter(Interface):
    """A device router object return plugin ID (i.e. a routing destination)
    from device objects.
    
    """
    
    def route(dev):
        """Return a plugin ID from a device object, or None if there's no
        route.
        
        dev -- either a device object or None.
        
        """


class PluginDeviceRouter(object):
    """A device router that return the 'plugin' key from the device object if
    it exists, or None in any other cases.
    
    """
    
    implements(IDeviceRouter)
    
    def route(self, dev):
        logger.debug('In %s', self.__class__.__name__)
        if dev is None:
            return None
        else:
            return dev.get('plugin')


class StaticDeviceRouter(object):
    """A device router that always return the same plugin ID.
    
    Note: can be used as a 'NullDeviceRouter' if 'self.pg_id is None'.
    
    """
    
    implements(IDeviceRouter)
    
    def __init__(self, pg_id=None):
        self.pg_id = pg_id
        
    def route(self, dev):
        logger.debug('In %s', self.__class__.__name__)
        return self.pg_id


class FirstCompositeDeviceRouter(object):
    """A composite device router that returns the first not None route ID."""
    
    implements(IDeviceRouter)
    
    def __init__(self, routers):
        self.routers = [] if routers is None else routers
        
    def route(self, dev):
        logger.debug('In %s', self.__class__.__name__)
        for router in self.routers:
            pg_id = router.route(dev)
            if pg_id is not None:
                return pg_id
        return None


# XXX should we leave the dev_mgr and other manager in this class or should
#     we inject them in the different 'handler' instances at create time ? This gives
#     a bit more flexibility and the different manager are long lived objects
#     (and if they change, we could add a level of indirection to them in a
#     server or something similar object)
class RequestProcessingService(object):
    """The base object responsible for dynamically modifying the process state
    when processing a request from a device.
    
    """
    dev_info_extractor = StaticDeviceInfoExtractor()
    dev_retriever = NullDeviceRetriever()
    dev_updater = NullDeviceUpdater()
    dev_router = StaticDeviceRouter()
    
    def __init__(self, app):
        self._app = app
        self._dev_mgr = app.dev_mgr
        self._cfg_mgr = app.cfg_mgr
        self._pg_mgr = app.pg_mgr
        self._req_id = 0    # used for logging
    
    def _new_req_id(self):
        req_id = "%d" % self._req_id
        self._req_id = (self._req_id + 1) % 100
        return req_id
    
    @defer.inlineCallbacks
    def process(self, request, ip, request_type):
        """Return a deferred that will eventually fire with a (dev, pg_id)
        pair:
        
        - dev is a device object or None, identifying which device is doing
          this request.
        - pg_id is a plugin identifier or None, identifying which plugin should
          continue to process this request.
        
        """
        req_id = self._new_req_id()
        logger.info('<%s> Processing %s request from %s', req_id, request_type, ip)
        
        # 1. Get a device info object
        logger.info('<%s> Extracting device info', req_id)
        d = self.dev_info_extractor.extract(request, request_type)
        dev_info = yield d
        if not dev_info:
            logger.warning('<%s> No device info extracted', req_id)
            dev_info = {'ip': ip}
        else:
            logger.info('<%s> Extracted device info: %s', req_id, dev_info)
            dev_info['ip'] = ip
        
        # 2. Get a device object
        assert dev_info['ip'] == ip
        logger.info('<%s> Retrieving device', req_id)
        dev = self.dev_retriever.retrieve(dev_info, self._app)
        if dev is None:
            logger.warn('<%s> No device retrieved', req_id)
        else:
            logger.info('<%s> Retrieved device: %s', req_id, dev)
        
        # 3. Update the device
        if dev is not None:
            logger.info('<%s> Updating device', req_id)
            # 3.1 Update the device
            reconfigure = self.dev_updater.update(dev, dev_info, request, request_type)
            
            # 3.2 Reconfigure the device
            if reconfigure:
                logger.info('<%s> Reconfiguring device: %s', req_id, dev)
                # XXX replace this with a call to an application object ?
                if 'config' in dev and 'plugin' in dev:
                    cfg_id = dev['config']
                    pg_id = dev['plugin']
                    if cfg_id not in self._cfg_mgr or pg_id not in self._pg_mgr:
                        # XXX log ?
                        pass
                    else:
                        pg = self._pg_mgr[pg_id]
                        cfg = self._cfg_mgr.flatten(cfg_id)
                        pg.configure(dev, cfg)
                
        
        # 4. Return a plugin ID
        logger.info('<%s> Finding route', req_id)
        pg_id = self.dev_router.route(dev)
        if pg_id is None:
            logger.warn('<%s> No route found', req_id)
        else:
            logger.info('<%s> Routing request to plugin %s', req_id, pg_id)
        defer.returnValue((dev, pg_id))


def _null_service_factory(pg_id, pg_service):
    return pg_service


class HTTPRequestProcessingService(Resource):
    """An HTTP service that does HTTP request processing and routing to
    the HTTP service of plugins.
    
    It's possible to add additional processing between this service and the
    plugin service by using a 'service factory' object which is a callable
    taking a plugin ID and a HTTP service and return a new service that will
    be used to continue with the processing of the request.
    
    Note that in the case the plugin doesn't offer an HTTP service, the
    'service factory' object is not used and the request is processed by
    the default service.
    
    If the process service returns an unknown plugin ID, a default service
    is used to continue with the request processing.
    
    """
    
    default_service = NoResource('Nowhere to route this request.')
    service_factory = _null_service_factory
    
    def __init__(self, process_service, pg_mgr):
        Resource.__init__(self)
        self._process_service = process_service
        self._pg_mgr = pg_mgr
    
    @defer.inlineCallbacks
    def getChild(self, path, request):
        ip = request.getClientIP()
        d = self._process_service.process(request, ip, 'http')
        dev, pg_id = yield d
        
        # Here we 'inject' the device object into the request object
        request.prov2_dev = dev

        service = self.default_service        
        if pg_id in self._pg_mgr:
            pg_service = self._pg_mgr[pg_id].http_service
            if pg_service is not None:
                service = self.service_factory(pg_id, pg_service)
        if service.isLeaf:
            request.postpath.insert(0, request.prepath.pop())
            defer.returnValue(service)
        else:
            defer.returnValue(service.getChildWithDefault(path, request))


class TFTPRequestProcessingService(object):
    """A TFTP read service that does TFTP request processing and routing to
    the TFTP read service of plugins.
    
    """
    
    default_service = TFTPNullService(errmsg="Nowhere to route this request")
    service_factory = _null_service_factory

    def __init__(self, process_service, pg_mgr):
        self._process_service = process_service
        self._pg_mgr = pg_mgr
    
    def handle_read_request(self, request, response):
        def aux((dev, pg_id)):
            # Here we 'inject' the device object into the request object
            request['prov2_dev'] = dev
            
            service = self.default_service
            if pg_id in self._pg_mgr:
                pg_service = self._pg_mgr[pg_id].tftp_service
                if pg_service is not None:
                    service = self.service_factory(pg_id, pg_service)
            service.handle_read_request(request, response)
            
        ip = request['address'][0]
        d = self._process_service.process(request, ip, 'tftp')
        d.addCallback(aux)
