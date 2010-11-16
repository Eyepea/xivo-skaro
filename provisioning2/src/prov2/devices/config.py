# -*- coding: UTF-8 -*-

"""Device configuration module.

Below is the list of 'standardized' parameters that can be found in
configuration mapping objects at the plugin level.

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
subscribemwi
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

# TODO delete the 2 next classes, replaced by simple dictionary objects and the
# flatten_config function
class Config(dict):
    """A configuration object... but more precisely...
    
    A dictionary that, when a lookup fail, will look into every of its
    fallback dictionaries.
    
    Note that only the get, __getitem__ and __contains__ methods have been
    overriden -- else it's a standard dictionary objects. This means you
    can have something like '2 in d'
    
    """
    cfg_manager = None
    
    def __init__(self):
        self.fallbacks = set()
        # fallbacks might not be the right word... a list of string
        # which represent configuration name of other dictionary
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            for fallback in self.fallbacks:
                # XXX there's a slight problem of exception hiding in the next
                # 2 lines... if the next line raise an exception but has been
                # called by this method in another object, the exception will
                # be hidden
                config = self.cfg_manager[fallback]
                try:
                    return config[key]
                except KeyError:
                    pass
        raise KeyError(key)
    
    def __contains__(self, item):
        try:
            self[item]
        except KeyError:
            return False
        else:
            return True


class ConfigManager(dict):
    def __setitem__(self, key, value):
        """Set an item and set this item configuration manager to
        this object...
        
        """
        value.cfg_manager = self
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        """Delete the item and remove all reference to this
        item from the other configuration objects.
        
        """
        dict.__delitem__(self, key)
        for config in self.itervalues():
            config.fallbacks.discard(key)


"""
A configuration object (config object) is a mapping object.

A configuration manager (config manager) is a mapping object where keys are
config object name and values are tuple (config object, sequence of config
object names).

"""

def list_config(cfg_manager, cfg_name):
    """Return a set of all the config object name that a config
    inherit directly or indirectly, excluding itself in any case.
    
    """
    visited = set()
    def aux(cur_cfg_name):
        if cur_cfg_name in visited:
            return
        visited.add(cur_cfg_name)
        cfg_base_names = cfg_manager[cur_cfg_name][1]
        for cfg_base_name in cfg_base_names:
            aux(cfg_base_name)

    aux(cfg_name)
    visited.remove(cfg_name)
    return visited


def _rec_update_dict(old_vals, new_vals):
    for k, v in new_vals.iteritems():
        if isinstance(v, dict):
            old_v = old_vals.get(k)
            if isinstance(old_v, dict):
                _rec_update_dict(old_v, v)
            else:
                old_vals[k] = v
        else:
            old_vals[k] = v


def flatten_config(cfg_manager, cfg_name):
    """Take a config manager and a config name and return a dictionary
    with all the items inherited from the base config. Dictionary object
    are correctly updated and not overriden.

    """

    # XXX what should we do with list ? I guess not treating them as a special case
    # is the right thing to do right now, especially that list can
    # be modeled as dictionary where keys are numbers
    res = {}
    def rec_flatten(cfg_name, visited):
        if cfg_name in visited:
            return
        visited.add(cfg_name)
        cfg, cfg_base_names = cfg_manager[cfg_name]
        for cfg_base_name in cfg_base_names:
            rec_flatten(cfg_base_name, visited.copy())
        _rec_update_dict(res, cfg)
    
    rec_flatten(cfg_name, set())
    return res
