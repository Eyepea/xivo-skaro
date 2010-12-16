# -*- coding: UTF-8 -*-

"""Device configuration module.

A configuration object (config object) is a mapping object, with value as defined
below.

A configuration manager (config manager) is a mapping object where keys are
config IDs (string) and values are tuple (config object, sequence of config
IDs).

Below is the list of 'standardized' parameters that can be found in
configuration objects at the plugin level.

TODO put more details about the type, valid values, optional/mandatory...
     and maybe put this at somewhere else (plugin module?)
XXX keys and values should be in unicode when applicable

proto
  The protocol to use. Current valid value are 'SIP' and 'SCCP'.
prov_ip
  The provisioning server IP address (dotted quad)
prov_http_port
  The provisioning server HTTP port number (default: 80)
ntp_server
  The NTP server IP address
admin_user
  The administrator username
admin_passwd
  The administrator password
timezone
  The timezone name (from the tz/zoneinfo/Olson database)
locale
  The locale name (ex.: fr_FR, en_US)
simultcalls
  The number of simultaneous calls (ex.: 5)
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
        user_id
          The user ID/username of this SIP identify.
        auth_id
          The auth ID used to authenticate
        passwd
          The password used to authenticate
        mailbox (?)
          The mailbox ID/number

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

import copy


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


class ConfigManager(dict):
    """A config manager manages config objects. Each config has an unique ID
    associated to it.
    
    """
    
    # XXX the req_graph currently doesn't work because the __setitem__
    #     and __delitem__ method aren't always called when an item is
    #     added/removed to the dict
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._req_graph = {}
    
    def _add_link(self, cfg_id):
        """Pre: cfg_id in self."""
        cfg = self[cfg_id]
        bases = cfg[1]
        for base in bases:
            self._req_graph.setdefault(base, set()).add(cfg_id)
        
    def _remove_link(self, cfg_id):
        """Pre: cfg_id in self."""
        cfg = self[cfg_id]
        bases = cfg[1]
        for base in bases:
            self._req_graph[base].remove(cfg_id)
    
    def __setitem__(self, cfg_id, cfg):
        # This doesn't work since dictionary are using the __setitem__
        # method not if you call update or call the constructor, etc,
        # should use composition instead...
        if cfg_id in self:
            self._remove_link(cfg_id)
        dict.__setitem__(self, cfg_id, cfg)
        self._add_link(cfg_id)
    
    def __delitem__(self, cfg_id):
        self._remove_link(cfg_id)
        dict.__delitem__(self, cfg_id)
    
    def list(self, cfg_id):
        """Return a list of config IDs for which every config is a direct or
        indirect dependency of cfg_id. The IDs are returned in the same order
        that the config would be flattened.
        
        """
        visited = set()
        def aux(cfg_id):
            if cfg_id in visited:
                return
            visited.add(cfg_id)
            bases = self[cfg_id][1]
            for base_cfg_id in bases:
                aux(base_cfg_id)
    
        aux(cfg_id)
        visited.remove(cfg_id)
        return visited
    
    def is_required(self, cfg_id):
#        return bool(self._req_graph.get(cfg_id))
        return bool(self.required_by(cfg_id))
    
    def required_by(self, cfg_id, maxdepth=-1):
        """Return a set of config IDs for which every config has a direct or
        indirect dependency on config cfg_id.
        
        Pre:  cfg_id in self
        Post: for id in self.required_by(cfg_id): cfg_id in self.list(id)
        
        """
#        return self._req_graph.get(cfg_id, set())
        # XXX Note that this is extremely inefficient
        # For example, if you have 1000 configs, and that 999 depends
        # on the same one, if you call required_by for this config,
        # it will make 1000 function calls and do 1000 * 1000 "__contains__"
        # tests.
        
        if cfg_id not in self:
            raise KeyError(cfg_id)
        visited = set()
        def aux(cfg_id, maxdepth):
            if cfg_id in visited:
                return
            visited.add(cfg_id)
            if maxdepth == 0:
                return
            maxdepth -= 1
            for cur_cfg_id, cur_cfg in self.iteritems():
                cur_bases = cur_cfg[1]
                if cfg_id in cur_bases:
                    aux(cur_cfg_id, maxdepth)
        
        aux(cfg_id, maxdepth)
        visited.remove(cfg_id)
        return visited
    
    def flatten(self, cfg_id):
        """Return a config object with every parameters from its bases config
        present.
        
        """
        res = {}
        visited = set()
        def rec_flatten(cur_cfg_id):
            if cur_cfg_id in visited:
                return
            visited.add(cur_cfg_id)
            cfg, cfg_base_ids = self[cur_cfg_id]
            for cfg_base_id in cfg_base_ids:
                rec_flatten(cfg_base_id)
            _rec_update_dict(res, cfg)
        
        rec_flatten(cfg_id)
        return res
    
    def remove(self, cfg_id):
        """Remove config with ID cfg_id from and then remove every reference to
        this config from the other configs.
        
        """ 
        del self[cfg_id]
        for _, cfg_base_ids in self.itervalues():
            if cfg_id in cfg_base_ids:
                cfg_base_ids.remove(cfg_id)
