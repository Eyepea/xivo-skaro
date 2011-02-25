# -*- coding: UTF-8 -*-

"""Config and config collection module.

Config objects are dictionaries, with the usual restrictions associated with
the fact they may be persisted in a document collection.

Config objects have the following standardized keys:
  id -- the IDs of this config object (unicode) (mandatory)
  parent_ids -- the IDs of parent config object (list of unicode) (mandatory)
  raw_config -- the configuration parameters of this config (dict) (mandatory)

Config collection objects are used as a storage for config objects.

"""

"""Specification of the configuration parameters.

This section specify the general form of configuration parameters and the
meaning and usage of standardized parameters.
  
This specification use the words MUST, SHOULD, MAY as defined in RFC2119.

Except when explicitly stated, unsupported parameters or supported parameters
with unsupported values SHOULD be ignored. For example, if your device has
no notion of timezone, or the plugin doesn't support configuring the timezone,
or the timezone value is not known from the plugin, then the timezone parameter
SHOULD be ignored and an exception SHOULD NOT be raised.

Parameter names are [unicode] string that MUST match the following regex:
[a-zA-Z_][a-zA-Z0-9_]*.

An IP address is a [unicode] string representing an IPv4 address in dotted
quad notation.

A port number is an integer between 1 and 65535 inclusive.

Beside each parameter definition is a specification telling if the parameter
must be found in the raw config passed to the plugin, and also specify what
the plugin can expect to receive.


ip [mandatory]
  The IP address or domain name of the provisioning server.
  If the followings are true:
  - this value represent a domain name
  - the device does not support the use of domain names
  then:
  - an exception (RawConfigError) MAY be raised or the device MAY be
    misconfigured.
  This means that if you use domain names, you should manually check that
  your devices support it or be prepared to see incorrect behaviour from
  your devices.

http_port [mandatory if tftp_port is not defined]
  The provisioning server HTTP port number.
  If the followings are true:
  - this value is defined
  - the device supports retrieving its configuration file via HTTP
  then:
  - the device MUST be configured to use HTTP to retrieve its configuration
    files (if applicable). If it does not support the port number value, it
    MUST raise an exception (RawConfigError).
  If the device only support HTTP yet this value is not defined, an Exception
  SHOULD be raised.

tftp_port [mandatory if http_port is not defined]
  The provisioning server TFTP port number.
  If the followings are true:
  - this value is defined
  - the device supports retrieving its configuration file via TFTP
  - the http_port parameter is not defined or the device does not support
    retrieving its configuration file via HTTP
  then:
  - the device MUST be configured to use TFTP to retrieve its configuration
    files (if applicable). If it does not support the port number value, it
    MUST raise an Exception.
  If the device only support TFTP yet this value is not defined, an Exception
  SHOULD be raised.

vlan [optional]
  A dictionary describing the VLAN (802.1Q) configuration.
  If this parameter is not defined, VLAN tagging MUST be disabled.
  
    id [mandatory]
      The VLAN ID. An integer between 0 and 4094.
      A value of 0 means that the frame does not belong to any VLAN; in this
      case only a priority is specified.
    
    priority [optional]
      The (802.1p) priority. A integer between 0 and 7 inclusive.

ntp_server [optional]
  The IP address or domain name of the NTP server.
  If this parameter is not defined, NTP MUST be disabled.
  See: ip (comment about domain name).

admin_username [optional]
  The administrator username. When applicable, the administrator account gives
  full access to the device (either via a web interface or a physical interface
  like a phone UI for example).

admin_password [optional]
  The administrator password.
  See: admin_username.

user_username [optional]
  The user username. When applicable, the user account gives limited access to
  the device.
  See: admin_username.

user_password [optional]
  The user password.
  See: admin_password.

timezone [optional]
  The name of the timezone from the tz/zoneinfo/Olson database.
  Example:
  - Europe/Paris
  - America/Montreal
  See: http://www.twinsun.com/tz/tz-link.htm.

locale [optional]
  The locale name. This is an ISO 639-1 code followed by an ISO 3166-1 alpha-2
  code. The codes are similar to what is found in /etc/locale.gen, except that
  it doesn't use the modifier and charset part.
  Example of possible values:
  - fr_FR
  - en_CA

protocol [mandatory]
  The signaling protocol.
  This parameter can take one of the following value:
  - SIP
  - SCCP
  If the protocol is not supported by the device, an exception
  (RawConfigError) MAY be raised or the device MAY be misconfigured.

sip [mandatory if protocol == 'SIP']
  A dictionary describing the configuration of all the SIP related stuff:
    
    dtmf_mode [optional]
      The mode used to send DTMF and other events.
      This parameter can take one of the following value:
      - RTP-in-band
      - RTP-out-of-band
      - SIP-INFO
      If this parameter is not defined and the device has some support for
      automatically picking the DTMF mode, then the device should be
      configured this way.
  
    subscribe_mwi [optional]
      A boolean indicating if we should explicitly subscribe for message
      notification or not.
    
    lines [optional|default to empty dictionary]
      A dictionary where keys are line number and values are dictionary with
      the following keys:
    
        proxy_ip [mandatory]
          The IP address of the SIP proxy.
          If the device does not support the proxy/registrar separation, the
          value of this parameter will be used as the registrar IP.
          # TODO eventually accept a domain name and some extra parameters
          #      to specify if we should do DNS SRV or DNS A/AAAA lookup. 
        
        backup_proxy_ip [optional]
          The IP address of the backup SIP proxy.
        
        registrar_ip [optional|default to value of proxy_ip]
          The IP address of the SIP registrar.
          See: proxy_ip.
        
        backup_registrar_ip [optional]
          The IP address of the backup SIP registrar
        
        outbound_proxy_ip [optional]
          The IP address of the SIP outbound proxy.
        
        username [mandatory]
          The username of this SIP identity.
        
        auth_username [optional|default to value of username]
          The username used for authentication (i.e. the username in the SIP
          Authorization or Proxy-Authorization header field).
          If the device doesn't allow the auth username to be different from
          the username, then the username MUST be used for authentication.
        
        password [mandatory]
          The password used for authentication.
        
        display_name [mandatory]
          The display name (caller ID).
        
        number [optional]
          The main extension number other users can dial to reach this line.
          This parameter is for display purpose only.
        
        dtmf_mode [optional]
          See: sip.dtmf_mode.
        
        voicemail [optional]
          The voicemail extension number for this line.

sccp [mandatory if protocol == 'SCCP']
  A dictionary describing the configuration of all the SCCP related stuff:
  
    call_managers [optional|default to empty dictionary]
      A dictionary where keys are priority number and value are dictionary
      with the following keys:
        
        ip [mandatory]
          The IP address of the call manager.
        
        port [optional]
          The port number of the call manager.

exten [optional|default to empty dictionary]
  A dictionary describing the available extension number:
  XXX this is not device configuration per se and until we have better support
  for references (for example, funckey referencing an extension), the value
  of this has yet to be seen. The only use right now is in templates.
  
    dnd [optional]
      The extension number to enable/disable 'do not disturb'.
    
    fwd_unconditional [optional]
      The extension number prefix to unable unconditional forward.
    
    fwd_no_answer [optional]
      The extension number prefix to unable forward on no-answer.
    
    fwd_busy [optional]
      The extension number prefix to unable forward on busy.
    
    fwd_disable_all [optional]
      The extension number prefix to disable every call forward.
    
    park [optional]
      The park extension number.
    
    pickup_group [optional]
      The extension number to pick up a call to a group.
    
    pickup_call [optional]
      The extension number prefix to pick up a call.
    
    voicemail [optional]
      The voicemail extension number.

funckeys [optional|default to empty dictionary]
  A dictionary where keys are function key number and values are dictionary:
  XXX this has to be reviewed (type/value vs exten/supervision ?)
    
    exten [mandatory]
      The extension number
    
    supervision [optional|default to false]
      A boolean indicating if we supervise this extension or not
    
    label [optional]
      The label.
    
    line [optional]
      The line number.

Non-standard parameter names must begin with 'X_'. A unique second level ID
should be used to prevent name clashes. Here's the list of parameters in
the 'X_xivo_' namespace:

X_xivo_extensions [optional]
  A boolean indicating if we should enable all the xivo-specific stuff.

X_xivo_phonebook_ip [optional]
  Remote XiVO phonebook service

Parameter names starting with 'XX_' must not be used in config object. They
must only be used as a way for a plugins to push/pass plugin specific values
to a template.

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

import copy
from provd.persist.common import ID_KEY
from provd.persist.util import ForwardingDocumentCollection
from twisted.internet import defer


class RawConfigError(Exception):
    """Raised when the raw config is not valid."""
    pass


class RawConfigParamError(RawConfigError):
    """Raised when a specific parameter of the raw config is not valid."""
    pass


def _rec_update_dict(base_dict, overlay_dict):
    # update a base dictionary from another dictionary
    for k, v in overlay_dict.iteritems():
        if isinstance(v, dict):
            old_v = base_dict.get(k)
            if isinstance(old_v, dict):
                _rec_update_dict(old_v, v)
            else:
                base_dict[k] = {}
                _rec_update_dict(base_dict[k], v)
        else:
            base_dict[k] = v


def _check_config_validity(config):
    # raise a value error if config is blatantly incorrect
    if u'parent_ids' not in config:
        raise ValueError('missing "parent_ids" field in config')
    elif not isinstance(config[u'parent_ids'], list):
        raise ValueError('"parent_ids" field must be a list; is %s' %
                         type(config[u'parent_ids']))
    if u'raw_config' not in config:
        raise ValueError('missing "raw_config" field in config')
    elif not isinstance(config[u'raw_config'], dict):
        raise ValueError('"raw_config" field must be a dict; is %s' %
                         type(config[u'raw_config']))


class ConfigCollection(ForwardingDocumentCollection):
    def __init__(self, collection):
        ForwardingDocumentCollection.__init__(self, collection)
        self._collection = collection
    
    def insert(self, config):
        _check_config_validity(config)
        return self._collection.insert(config)
    
    def update(self, config):
        _check_config_validity(config)
        return self._collection.update(config)
    
    def get_ancestors(self, id):
        """Return a deferred that will fire with the set of ancestors of the
        config with the given ID, i.e. the set of config ID that the given
        config depends on, directly or indirectly, or fire with None if id
        is an unknown id.
        
        """
        visited = set()
        @defer.inlineCallbacks
        def aux(cur_id):
            if cur_id in visited:
                return
            visited.add(cur_id)
            config = yield self._collection.retrieve(cur_id)
            if config is not None:
                for parent_id in config[u'parent_ids']:
                    yield aux(parent_id)
    
        def on_success(_):
            visited.remove(id)
            # visited will now be empty if id is unknown
            return visited or None
        d = aux(id)
        d.addCallback(on_success)
        return d
    
    def has_descendants(self, id):
        """Return a deferred that will fire with true if the config with the
        given ID has any descendants, else will fire with false.
        
        """
        return self.get_descendants(id, maxdepth=1)
    
    def get_descendants(self, id, maxdepth=-1):
        """Return a deferred that will fire with the set of descendants of the
        config with the given ID, i.e. the set of config ID that depends on
        this config, directly or indirectly. 
        
        """
        visited = set()
        @defer.inlineCallbacks
        def aux(cur_id, maxdepth):
            if cur_id in visited:
                return
            visited.add(cur_id)
            if maxdepth == 0:
                return
            maxdepth -= 1
            configs = yield self._collection.find({u'parent_ids': cur_id}) 
            for config in configs:
                assert cur_id in config[u'parent_ids']
                yield aux(config[ID_KEY], maxdepth)
        
        def on_success(_):
            visited.remove(id)
            return visited
        d = aux(id, maxdepth)
        d.addCallback(on_success)
        return d
    
    def get_raw_config(self, id, base_raw_config={}):
        """Return a deferred that will fire with a raw config with every
        parameters from its ancestors config, or fire with None if id is not
        a known ID.
        
        """
        # flattened_raw_config is set to a copy of base_raw_config only once
        # we know that the id is valid. This is a bit ugly, but it's the
        # simplest thing to do.
        # Also, flattened_raw_config is a list since we don't have a nonlocal
        # statement like in python3, and can't rebind the name in an inner
        # scope...
        flattened_raw_config = [None]
        visited = set()
        @defer.inlineCallbacks
        def aux(cur_id):
            if cur_id in visited:
                return
            visited.add(cur_id)
            config = yield self._collection.retrieve(cur_id)
            if config is not None:
                if flattened_raw_config[0] is None:
                    flattened_raw_config[0] = copy.deepcopy(base_raw_config)
                for base_id in config[u'parent_ids']:
                    yield aux(base_id)
                _rec_update_dict(flattened_raw_config[0], config[u'raw_config'])
        
        d = aux(id)
        d.addCallback(lambda _: flattened_raw_config[0])
        return d

    @defer.inlineCallbacks
    def delete_references(self, id):
        """Delete all the references to the config with the given ID, i.e.
        for each config with has the given config has a parent, remove the
        given config from its 'parent_ids' key.
        
        Return a deferred that will fire with None once the operation has
        been completed.
        
        """
        configs = yield self._collection.find({u'parent_ids': id})
        for config in configs:
            config[u'parent_ids'].remove(id)
            yield self._collection.update(config)
