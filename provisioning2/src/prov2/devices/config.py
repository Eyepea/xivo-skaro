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
    def list(self, cfg_id):
        """Return the sequence of base config IDs of a config."""
        visited = set()
        def aux(cur_cfg_id):
            if cur_cfg_id in visited:
                return
            visited.add(cur_cfg_id)
            cfg_base_ids = self[cur_cfg_id][1]
            for cfg_base_id in cfg_base_ids:
                aux(cfg_base_id)
    
        aux(cfg_id)
        visited.remove(cfg_id)
        return visited
    
    def flatten(self, cfg_id):
        """Return a config object with every parameters from its bases config
        present.
        
        """
        res = {}
        def rec_flatten(cur_cfg_id, visited):
            if cur_cfg_id in visited:
                return
            visited.add(cur_cfg_id)
            cfg, cfg_base_ids = self[cur_cfg_id]
            for cfg_base_id in cfg_base_ids:
                rec_flatten(cfg_base_id, visited.copy())
            _rec_update_dict(res, cfg)
        
        rec_flatten(cfg_id, set())
        return res
    
    def remove(self, cfg_id):
        """Remove config with ID cfg_id from and then remove every reference to
        this config from the other configs.
        
        """ 
        del self[cfg_id]
        for _, cfg_base_ids in self.itervalues():
            if cfg_id in cfg_base_ids:
                cfg_base_ids.remove(cfg_id)
