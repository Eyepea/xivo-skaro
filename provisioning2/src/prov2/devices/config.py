# -*- coding: UTF-8 -*-

"""Config and config collection module.

Config objects are dictionaries, with the usual restrictions associated with
the fact they may be persisted in a document collection.

Config objects have the following standardized keys:
  id -- the IDs of this config object (unicode) (mandatory)
  parent_ids -- the IDs of parent config object (list of unicode) (mandatory)
  raw_config -- the configuration parameters of this config (dict) (mandatory)

Config collection objects are used as a storage for config objects.

Below is the list of 'standardized' parameters that can be found in raw
configuration objects at the plugin level.

Note that every time you see a string or see a reference to a string, think
about a unicode string, and not a python 'byte' string. This is true for keys
and values. 

TODO put more details about the type, valid values, optional/mandatory...

An IP address is a string IPv4 address in dotted quad notation.
A port number is an integer between 1 and 65535 inclusive.

ip
  The provisioning server IP address. Always present.
http_port
  The provisioning server HTTP port number. Always present.
tftp_port
  The provisioning server TFTP port number. Always present.

proto
  The protocol to use. Current valid value are 'SIP' and 'SCCP'.
ntp_server
  The NTP server IP address.
admin_user
  The administrator username. This is an unicode string.
admin_passwd
  The administrator password. This is an unicode string.
timezone
  The timezone name (from the tz/zoneinfo/Olson database).
  - Ex.: 'Europe/Paris', 'America/Montreal'
locale
  The locale name. This is an ISO 639-1 code followed by an ISO 3166-1 alpha-2
  code. The codes are similar to what is found in /etc/locale.gen, except that
  it doesn't use the modifier and charset part.
  - Ex.: 'fr_FR', 'en_CA'
simultcalls
  The number of simultaneous calls (ex.: 5). This is a positive integer.
subscribe_mwi
  A boolean for if we should subscribe for message notification or not

vlan
  A dictionary with the following keys
    enabled
      A flag indicating if VLAN is enabled
    id
      The VLAN ID
    prio
      The priority

sip
  A dictionary with the following keys
    dtmfmode
      The DTMF mode
    lines
      A dictionary where keys are line number and value are dictionary with
      the following keys:
    
        proxy_ip
          The proxy IP address
        backup_proxy_ip
          The backup proxy IP
        registrar_ip
          The registrar IP address
        backup_registrar_ip
          The backup registrar IP
        outbound_proxy_ip
          The outbound proxy IP
        display_name
          The display name for caller ID
        number
          The extension number
        user_id
          The user ID/username of this SIP identify.
        auth_id
          The auth ID used to authenticate
        passwd
          The password used to authenticate
        mailbox (?)
          The mailbox ID/number

sccp
  A dictionary with the following keys
    call_managers
      A dictionary where keys are priority number and value are dictionary
      with the following keys:
        
        ip
          The call manager IP address
        port
          The call manager port number (default: 2000)

exten
  A dictionary with the following keys
    dnd
      The DND enable/disable extension number
    pickup
      The pickup extension number
    pickup_prefix
      The pickup prefix
    fwdunc
      The unconditional forward extension number
    park
      The park extension number
    voicemail
      The voicemail extension number

funckey
  A dictionary where keys are function key number and values are dictionary:
    exten
      The extension number
    supervision
      A boolean indicating if we supervise this extension or not
    label
      The label
    line
      The line number

Non-standard parameters should begin with 'X_'. A unique second level ID 
should be used to prevent name clashes. Here's the list of parameters in
the 'X_xivo_' namespace:

X_xivo_phonebook_ip
  Remote XiVO phonebook service
X_xivo_extensions
  A boolean which value is true if we should enable all the xivo-specific stuff,
  else false
X_xivo_bg_picture
  URI of a background picture

Parameters starting with 'XX_' should not be used in configuration mapping
objects. They are reserved as a way for plugin to push/pass plugin specific
value to a template.

Parameters should be valid python identifiers since it should be possible to
use them directly using the standard template format.

"""
from twisted.internet import defer

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
from prov2.persist.common import ID_KEY
from prov2.persist.util import ForwardingDocumentCollection


def _rec_update_dict(old_vals, new_vals):
    for k, v in new_vals.iteritems():
        if isinstance(v, dict):
            old_v = old_vals.get(k)
            if isinstance(old_v, dict):
                _rec_update_dict(old_v, v)
            else:
                old_vals[k] = copy.deepcopy(v)
                ## This also works if we don't want to use deepcopy:
                #old_vals[k] = {}
                #_rec_update_dict(old_vals[k], v)
        else:
            old_vals[k] = v


class ConfigCollection(ForwardingDocumentCollection):
    def __init__(self, collection):
        ForwardingDocumentCollection.__init__(self, collection)
        self._collection = collection
    
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
        flattened_raw_config = None
        visited = set()
        @defer.inlineCallbacks
        def aux(cur_id):
            if cur_id in visited:
                return
            visited.add(cur_id)
            config = yield self._collection.retrieve(cur_id)
            if config is not None:
                if flattened_raw_config is None:
                    copy.deepcopy(base_raw_config)
                for base_id in config[u'parent_ids']:
                    yield aux(base_id)
                _rec_update_dict(flattened_raw_config, config[u'raw_config'])
        
        d = aux(id)
        d.addCallback(lambda _: flattened_raw_config)
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
