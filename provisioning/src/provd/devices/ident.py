# -*- coding: UTF-8 -*-

"""Request processing service definition."""

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
import logging
from operator import itemgetter
from provd.persist.common import ID_KEY
from provd.plugins import BasePluginManagerObserver
from provd.servers.tftp.packet import ERR_UNDEF
from provd.servers.tftp.service import TFTPNullService
from provd.util import norm_ip
from twisted.internet import defer
from twisted.web.http import INTERNAL_SERVER_ERROR
from twisted.web.resource import Resource, NoResource, ErrorPage
from zope.interface import Interface, implements

logger = logging.getLogger(__name__)


class IDeviceInfoExtractor(Interface):
    """A device info extractor object extract device information from
    requests. In our context, requests are either HTTP, TFTP or DHCP
    requests.
    
    Example of information that can be extracted are:
    - IP address
    - MAC address
    - vendor name
    - model name
    - version number
    - serial number
    
    Note: DHCP requests are not processed by the provisioning server per se.
    The provisioning server use them only to get information from it and update
    the corresponding device object. For example, with a valid source of DHCP
    information, we can then always make sure the IP <-> MAC for a device is
    up to date. 
    
    """

    def extract(request, request_type):
        """Return a deferred that will fire with either an non empty
        device info object or an object that evaluates to false in a boolean
        context if no information could be extracted.
        
        So far, request_type is either 'http', 'tftp' or 'dhcp'. See the
        various {HTTP,TFTP,DHCP}RequestProcessingService for more information
        about the type of each request.
        
        """


class StandardDeviceInfoExtractor(object):
    """Device info extractor that return standard and readily available
    information from requests, like IP addresses, or MAC addresses for DHCP
    requests.
    
    You SHOULD always use this extractor.
    
    """

    implements(IDeviceInfoExtractor)

    def _extract_tftp(self, request):
        return {u'ip': norm_ip(request['address'][0].decode('ascii'))}

    def _extract_http(self, request):
        return {u'ip': norm_ip(request.getClientIP().decode('ascii'))}

    def _extract_dhcp(self, request):
        return {u'ip': request[u'ip'], u'mac': request[u'mac']}

    def extract(self, request, request_type):
        logger.debug('In StandardDeviceInfoExtractor')
        method_name = '_extract_%s' % request_type
        try:
            method = getattr(self, method_name)
        except AttributeError:
            logger.warning('No extract method for request type %s', request_type)
            return defer.succeed(None)
        else:
            return defer.succeed(method(request))


class StaticDeviceInfoExtractor(object):
    """Device info extractor that always return the same device information."""

    implements(IDeviceInfoExtractor)

    def __init__(self, dev_info):
        self._dev_info = dev_info

    def extract(self, request, request_type):
        logger.debug('In StaticDeviceInfoExtractor')
        return defer.succeed(self._dev_info)


def NullDeviceInfoExtractor():
    """Device info extractor that always return None."""
    return StaticDeviceInfoExtractor(None)


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
        logger.debug('In FirstCompositeDeviceInfoExtractor')
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
        logger.debug('In LongestDeviceInfoExtractor')
        dlist = defer.DeferredList([extractor.extract(request, request_type)
                                    for extractor in self.extractors])
        dlist_results = yield dlist
        dev_info, length = None, 0
        for success, result in dlist_results:
            if success and result and len(result) > length:
                dev_info, length = result, len(result)
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
        for k, v in conflicts.iteritems():
            if v != self.dev_info[k]:
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
        return max(key_pool.iteritems(), key=itemgetter(1))[0]

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
        logger.debug('In CollaboratingDeviceInfoExtractor')
        dlist = defer.DeferredList([extractor.extract(request, request_type)
                                    for extractor in self.extractors])
        dlist_results = yield dlist
        updater = self._updater_factory()
        for success, result in dlist_results:
            if success and result:
                updater.update(result)
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
        # observe plugin loading/unloading and keep a reference to the weakly
        # referenced observer
        self._obs = BasePluginManagerObserver(self._on_plugin_load_or_unload,
                                              self._on_plugin_load_or_unload)
        pg_mgr.attach(self._obs)

    def _set_pg(self):
        self._pg = self._pg_mgr.get(self._pg_id)

    def _on_plugin_load_or_unload(self, pg_id):
        self._set_pg()

    def extract(self, request, request_type):
        logger.debug('In PluginDeviceInfoExtractor')
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

    _REQUEST_TYPES = ['http', 'tftp', 'dhcp']

    def __init__(self, extractor_factory, pg_mgr):
        """
        extractor_factory -- a function taking a list of extractors and
          returning an extractor.
        """
        self.extractor_factory = extractor_factory
        self._pg_mgr = pg_mgr
        self._set_xtors()
        # observe plugin loading/unloading and keep a reference to the weakly
        # referenced observer
        self._obs = BasePluginManagerObserver(self._on_plugin_load_or_unload,
                                              self._on_plugin_load_or_unload)
        pg_mgr.attach(self._obs)

    def _xtor_name(self, request_type):
        return '_%s_xtor' % request_type

    def _set_xtors(self):
        logger.debug('Updating extractors for %s', self)
        for request_type in self._REQUEST_TYPES:
            pg_extractors = []
            for pg in self._pg_mgr.itervalues():
                pg_extractor = getattr(pg, request_type + '_dev_info_extractor')
                if pg_extractor is not None:
                    logger.debug('Adding %s extractor from %s', request_type, pg)
                    pg_extractors.append(pg_extractor)
            xtor = self.extractor_factory(pg_extractors)
            setattr(self, self._xtor_name(request_type), xtor)

    def _on_plugin_load_or_unload(self, pg_id):
        self._set_xtors()

    def extract(self, request, request_type):
        logger.debug('In AllPluginsDeviceInfoExtractor')
        xtor = getattr(self, self._xtor_name(request_type))
        return xtor.extract(request, request_type)


class IDeviceRetriever(Interface):
    """A device retriever return a device object from device information.
    
    Instances providing this interface MAY have some side effect on the
    application, like adding a new device.
    
    """

    def retrieve(dev_info):
        """Return a deferred that will fire with either a device object
        or None if it can't find such object.
        
        """


class NullDeviceRetriever(object):
    """Device retriever who never retrieves anything."""
    implements(IDeviceRetriever)

    def retrieve(self, dev_info):
        logger.debug('In NullDeviceRetriever')
        return defer.succeed(None)


class SearchDeviceRetriever(object):
    """Device retriever who search in the application for a device with a
    key's value the same as a device info key's value, and return the first
    one found.
    
    """

    implements(IDeviceRetriever)

    def __init__(self, app, key):
        self._app = app
        self._key = key

    def retrieve(self, dev_info):
        logger.debug('In SearchDeviceRetriever')
        if self._key in dev_info:
            return self._app.dev_find_one({self._key: dev_info[self._key]})
        return defer.succeed(None)


class IpDeviceRetriever(object):
    implements(IDeviceRetriever)

    def __init__(self, app):
        self._app = app

    @defer.inlineCallbacks
    def retrieve(self, dev_info):
        logger.debug('In IpDeviceRetriever')
        if u'ip' in dev_info:
            devices = yield self._app.dev_find({u'ip': dev_info[u'ip']})
            matching_device = self._get_matching_device(devices, dev_info)
            defer.returnValue(matching_device)
        defer.returnValue(None)

    def _get_matching_device(self, devices, dev_info):
        candidate_devices = self._get_candidate_devices(devices, dev_info)
        nb_candidates = len(candidate_devices)
        if nb_candidates == 1:
            return candidate_devices[0]
        elif nb_candidates > 1:
            logger.warning('Multiple device match in IP device retriever: %r', candidate_devices)
        return None

    def _get_candidate_devices(self, devices, dev_info):
        devices_by_id = dict((device[u'id'], device) for device in devices)
        self._filter_devices_by_key(devices_by_id, dev_info, u'mac')
        self._filter_devices_by_key(devices_by_id, dev_info, u'vendor')
        self._filter_devices_by_key(devices_by_id, dev_info, u'model')
        return devices_by_id.values()

    def _filter_devices_by_key(self, devices_by_id, dev_info, key):
        if key in dev_info:
            key_value = dev_info[key]
            for device in devices_by_id.values():
                if key in device:
                    if device[key] != key_value:
                        device_id = device[u'id']
                        del devices_by_id[device_id]


def MacDeviceRetriever(app):
    """Retrieve device object by looking up in a device manager for an
    object which MAC is the same as the device info object.
    
    """
    return SearchDeviceRetriever(app, u'mac')


def SerialNumberDeviceRetriever(app):
    """Retrieve device object by looking up in a device manager for an
    object which serial number is the same as the device info object.
    
    """
    return SearchDeviceRetriever(app, u'sn')


def UUIDDeviceRetriever(app):
    """Retrieve device object by looking up in a device manager for an
    object which UUID is the same as the device info object.
    
    """
    return SearchDeviceRetriever(app, u'uuid')


class AddDeviceRetriever(object):
    """A device retriever that does no lookup and always insert a new device
    in the application.
    
    Mostly useful if used in a FirstCompositeDeviceRetriever at the end of
    the list, in a way that it will be called only if the other retrievers
    don't find anything.
    
    """

    implements(IDeviceRetriever)

    def __init__(self, app):
        self._app = app

    def retrieve(self, dev_info):
        logger.debug('In AddDeviceRetriever')
        device = copy.deepcopy(dev_info)
        device[u'added'] = u'auto'
        d = self._app.dev_insert(device)
        d.addCallbacks(lambda _: device, lambda _: None)
        return d


class FirstCompositeDeviceRetriever(object):
    """Composite device retriever which return the device its first retriever
    returns.
    
    """

    implements(IDeviceRetriever)

    def __init__(self, retrievers=None):
        self.retrievers = [] if retrievers is None else retrievers

    @defer.inlineCallbacks
    def retrieve(self, dev_info):
        logger.debug('In FirstCompositeDeviceRetriever')
        retrievers = self.retrievers[:]
        for retriever in retrievers:
            device = yield retriever.retrieve(dev_info)
            if device is not None:
                defer.returnValue(device)
        defer.returnValue(None)


class IDeviceUpdater(Interface):
    """Update a device object device from an info object.
    
    This operation can have side effect, like updating the device. In fact,
    being able to do side effects is why this interface exist.

    """

    def update(device, dev_info, request, request_type):
        """Update a device object, returning a deferred that will fire once
        the device object has been updated, with either true if the device
        should be forced to be reconfigured, else false.
        
        Forcing device reconfiguration is only useful if you are using some
        non standard keys. Device reconfiguration is normally automatically
        handled.
        
        device -- a nonempty device object
        dev_info -- a potentially empty device info object
        
        """


class NullDeviceUpdater(object):
    """Device updater that updates nothing."""

    implements(IDeviceUpdater)

    def update(self, device, dev_info, request, request_type):
        logger.debug('In NullDeviceUpdater')
        return defer.succeed(False)


class StaticDeviceUpdater(object):
    """Device updater that updates one of the device key with a fixed value.
    
    If the key is already present in the device, then the device will be
    updated only if force_update is true.
    
    Its update method always return false, i.e. does not force a device
    reconfiguration.
    
    """

    implements(IDeviceUpdater)

    def __init__(self, key, value, force_update=False):
        self._key = key
        self._value = value
        self._force_update = force_update

    def update(self, device, dev_info, request, request_type):
        logger.debug('In StaticDeviceUpdater')
        if self._force_update or self._key not in device:
            device[self._key] = self._value
        return defer.succeed(False)


class DynamicDeviceUpdater(object):
    """Device updater that updates zero or more of the device key with the
    value of the device info key.
    
    If the key is already present in the device, then the device will be
    updated only if force_update is true.
    
    Its update method always return false, i.e. does not force a device
    reconfiguration.
    
    """

    implements(IDeviceUpdater)

    def __init__(self, keys, force_update=False):
        # keys can either be a string (i.e. u'ip') or a list of string
        #   (i.e. [u'ip', u'version'])
        if isinstance(keys, basestring):
            keys = [keys]
        self._keys = list(keys)
        self._force_update = force_update

    def update(self, device, dev_info, request, request_type):
        logger.debug('In DynamicDeviceUpdater')
        for key in self._keys:
            if key in dev_info:
                if self._force_update or key not in device:
                    device[key] = dev_info[key]
        return defer.succeed(False)


class AddInfoDeviceUpdater(object):
    """Device updater that add any missing information to the device from
    the device info.
    
    Its update method always return false, i.e. does not force a device
    reconfiguration.
    
    """

    implements(IDeviceUpdater)

    def update(self, device, dev_info, request, request_type):
        logger.debug('In AddInfoDeviceUpdater')
        for key in dev_info:
            if key not in device:
                device[key] = dev_info[key]
        return defer.succeed(False)


class ReplaceDeviceUpdater(object):
    """Device updater that replace the device with the device info.
    
    This SHOULD NOT be used in normal situation.
    
    """

    implements(IDeviceUpdater)

    def update(self, device, dev_info, request, request_type):
        logger.debug('In ReplaceDeviceUpdater')
        device.clear()
        device.update(copy.deepcopy(dev_info))
        return defer.succeed(False)


def IpDeviceUpdater():
    """Device updater that updates the IP address."""
    return DynamicDeviceUpdater(u'ip', True)


class VersionDeviceUpdater(object):
    """If 'model' in dev and 'version' in dev_info, then update dev['version']
    to dev_info['version'].
    
    """

    implements(IDeviceUpdater)

    delete_on_no_version = True

    def update(self, device, dev_info, request, request_type):
        logger.debug('In VersionDeviceUpdater')
        if u'vendor' in device and u'model' in device:
            if u'version' in dev_info:
                device[u'version'] = dev_info[u'version']
            else:
                if self.delete_on_no_version and u'version' in device:
                    del device[u'version']
        return defer.succeed(False)


class DefaultConfigDeviceUpdater(object):
    """Device updater that set a default config to the device if the device
    has no config.
    
    The way it works is that when a device with no config is found, a search
    for a config with type 'default' is done and the first config found is
    associated with the device.
    
    """
    def __init__(self, app):
        self._app = app

    @defer.inlineCallbacks
    def update(self, device, dev_info, request, request_type):
        logger.debug('In DefaultConfigDeviceUpdater')
        if u'config' not in device:
            config = yield self._app.cfg_find_one({u'role': u'default'})
            if config:
                device[u'config'] = config[ID_KEY]
            else:
                logger.warning('No config with the default role found')
        defer.returnValue(False)


class AutocreateConfigDeviceUpdater(object):
    """Device updater that set an autocreated config to the device if the
    device has no config.
    
    """
    def __init__(self, app):
        self._app = app

    @defer.inlineCallbacks
    def update(self, device, dev_info, request, request_type):
        logger.debug('In AutocreateConfigDeviceUpdater')
        if u'config' not in device:
            new_config_id = yield self._app.cfg_create_new()
            if new_config_id is not None:
                device[u'config'] = new_config_id
        defer.returnValue(False)


class RemoveOutdatedIpDeviceUpdater(object):
    def __init__(self, app):
        self._app = app

    @defer.inlineCallbacks
    def update(self, device, dev_info, request, request_type):
        logger.debug('In RemoveOutdatedIpDeviceUpdater')
        if u'ip' in dev_info:
            selector = {u'ip': dev_info[u'ip'], u'id': {'$ne': device[u'id']}}
            outdated_devices = yield self._app.dev_find(selector)
            for outdated_device in outdated_devices:
                del outdated_device[u'ip']
                self._app.dev_update(outdated_device)


class CompositeDeviceUpdater(object):
    implements(IDeviceUpdater)

    def __init__(self, updaters=None):
        self.updaters = [] if updaters is None else updaters

    @defer.inlineCallbacks
    def update(self, device, dev_info, request, request_type):
        logger.debug('In CompositeDeviceUpdater')
        force_reconfigure = False
        for updater in self.updaters:
            d = updater.update(device, dev_info, request, request_type)
            force_reconfigure = (yield d) or force_reconfigure
        defer.returnValue(force_reconfigure)


class IDeviceRouter(Interface):
    """A device router object return plugin ID (i.e. a routing destination)
    from device objects.
    
    """

    def route(device, dev_info):
        """Return a plugin ID from a device object, or None if there's no
        route.
        
        device -- either a device object or None.
        dev_info -- a potentially empty device info object
        
        """


class PluginDeviceRouter(object):
    """A device router that return the 'plugin' key from the device object if
    it exists, or None in any other cases.
    
    """

    implements(IDeviceRouter)

    def route(self, device, dev_info):
        logger.debug('In PluginDeviceRouter')
        if device is None:
            return None
        else:
            return device.get(u'plugin')


class StaticDeviceRouter(object):
    """A device router that always returns the same plugin ID."""

    implements(IDeviceRouter)

    def __init__(self, pg_id):
        self._pg_id = pg_id

    def route(self, device, dev_info):
        logger.debug('In StaticDeviceRouter')
        return self._pg_id


def NullDeviceRouter():
    """A device router that always returns None."""
    return StaticDeviceRouter(None)


class FirstCompositeDeviceRouter(object):
    """A composite device router that returns the first not None route ID."""

    implements(IDeviceRouter)

    def __init__(self, routers):
        self.routers = [] if routers is None else routers

    def route(self, device, dev_info):
        logger.debug('In FirstCompositeDeviceRouter')
        for router in self.routers:
            pg_id = router.route(device, dev_info)
            if pg_id is not None:
                return pg_id
        return None


class RequestProcessingService(object):
    """The base object responsible for dynamically modifying the process state
    when processing a request from a device.
    
    """
    dev_info_extractor = NullDeviceInfoExtractor()
    dev_retriever = NullDeviceRetriever()
    dev_updater = NullDeviceUpdater()
    dev_router = NullDeviceRouter()

    def __init__(self, app):
        self._app = app
        self._req_id = 0    # used for logging

    def _new_request_id(self):
        req_id = "%d" % self._req_id
        self._req_id = (self._req_id + 1) % 100
        return req_id

    @defer.inlineCallbacks
    def process(self, request, request_type):
        """Return a deferred that will eventually fire with a (device, pg_id)
        pair, where:
        
        - device is a device object or None, identifying which device is doing
          this request.
        - pg_id is a plugin identifier or None, identifying which plugin should
          continue to process this request.
        
        """
        req_id = self._new_request_id()

        # 1. Get a device info object
        logger.debug('<%s> Extracting device info', req_id)
        dev_info = yield self.dev_info_extractor.extract(request, request_type)
        if not dev_info:
            logger.info('<%s> No device info extracted', req_id)
            dev_info = {}
        else:
            logger.info('<%s> Extracted device info: %s', req_id, dev_info)

        # 2. Get a device object
        logger.debug('<%s> Retrieving device', req_id)
        device = yield self.dev_retriever.retrieve(dev_info)
        if device is None:
            logger.info('<%s> No device retrieved', req_id)
        else:
            logger.info('<%s> Retrieved device id: %s', req_id, device[u'id'])

        # 3. Update the device
        if device is not None:
            logger.debug('<%s> Updating device', req_id)
            # 3.1 Update the device
            orig_device = copy.deepcopy(device)
            force_reconfigure = yield self.dev_updater.update(device, dev_info,
                                                              request, request_type)

            # 3.2 Persist the modification if there was a change
            if device != orig_device:
                logger.info('<%s> Device has been updated', req_id)
                yield self._app.dev_update(device)

            # 3.3 Reconfigure the device if needed
            # XXX we should check that the call to _app.dev_update did not lead
            #     to a device reconfiguration; if this is the case, we should
            #     not reconfigure the device (i.e. this is inefficient)
            if force_reconfigure:
                logger.info('<%s> Reconfiguring device', req_id)
                self._app.dev_reconfigure(device[ID_KEY])

        # 4. Return a plugin ID
        logger.debug('<%s> Finding route', req_id)
        pg_id = self.dev_router.route(device, dev_info)
        if pg_id is None:
            logger.info('<%s> No route found', req_id)
        else:
            logger.info('<%s> Routing request to plugin %s', req_id, pg_id)
        defer.returnValue((device, pg_id))


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

    # implements(IHTTPService)

    default_service = NoResource('Nowhere to route this request.')

    def __init__(self, process_service, pg_mgr):
        Resource.__init__(self)
        self._process_service = process_service
        self._pg_mgr = pg_mgr
        self.service_factory = _null_service_factory

    @defer.inlineCallbacks
    def getChild(self, path, request):
        logger.info('Processing HTTP request: %s', request.path)
        logger.debug('HTTP request: %s', request)
        try:
            device, pg_id = yield self._process_service.process(request, 'http')
        except Exception:
            logger.error('Error while processing HTTP request:', exc_info=True)
            defer.returnValue(ErrorPage(INTERNAL_SERVER_ERROR,
                              'Internal processing error',
                              'Internal processing error'))
        else:
            # Here we 'inject' the device object into the request object
            request.prov_dev = device

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

    # implements(ITFTPReadService)

    default_service = TFTPNullService(errmsg="Nowhere to route this request")

    def __init__(self, process_service, pg_mgr):
        self._process_service = process_service
        self._pg_mgr = pg_mgr
        self.service_factory = _null_service_factory

    def handle_read_request(self, request, response):
        logger.info('Processing TFTP request: %s', request['packet']['filename'])
        logger.debug('TFTP request: %s', request)
        def callback((device, pg_id)):
            # Here we 'inject' the device object into the request object
            request['prov_dev'] = device

            service = self.default_service
            if pg_id in self._pg_mgr:
                pg_service = self._pg_mgr[pg_id].tftp_service
                if pg_service is not None:
                    service = self.service_factory(pg_id, pg_service)
            service.handle_read_request(request, response)
        def errback(failure):
            logger.error('Error while processing TFTP request: %s', failure)
            response.reject(ERR_UNDEF, 'Internal processing error')
        d = self._process_service.process(request, 'tftp')
        d.addCallbacks(callback, errback)


class DHCPRequestProcessingService(Resource):
    """A DHCP request service that does DHCP request processing.
    
    Contrary to the HTTP/TFTP request processing service, this service does
    not route the request to a plugin specific DHCP request service, since
    there's no such thing. It is only used to process DHCP request to
    extract information from it and potentially update affected device
    objects.
    
    Also, in this context, these are not real DHCP request, but more like
    DHCP transaction information objects. We use the term request for
    homogeneity sake.
    
    """
    def __init__(self, process_service):
        self._process_service = process_service

    def handle_dhcp_request(self, request):
        """Handle DHCP request.
        
        DHCP requests are dictionary objects with the following keys:
          u'ip' -- the IP address of the client who made the request, in
            normalized format
          u'mac' -- the MAC address of the client who made the request, in
            normalized format
          u'options' -- a dictionary of client options, where keys are integers
            representing the option code, and values are byte string
            representing the raw value of the option
        """
        logger.info('Processing DHCP request: %s', request[u'ip'])
        logger.debug('DHCP request: %s', request)
        def errback(failure):
            logger.error('Error while processing DHCP request: %s', failure)
        d = self._process_service.process(request, 'dhcp')
        d.addErrback(errback)
