# -*- coding: UTF-8 -*-

"""Device-related stuff module...

A device info object is a mapping object with the following keys:
  mac -- the normalized MAC address of this device 
  ip -- the (last seen) normalized IP address of this device
  vendor -- the vendor name of this device (string)
  model -- the model name of this device (string)
  version -- the version of the software/firmware of this device (string)
XXX since it's theoretically possible for some device to be used with different software,
    and in these cases a 'version' field is not enough to identify which software its
    using, we might want to add another field like 'firmware' or change the semantic and
    the name of the 'version' field to include not only the version but the firmware name/id

A device object is a device info object + the followings keys:
  plugin -- the name of the plugin this device is managed by (string)
  config -- the name of the configuration of this device (string)

The most meaningful difference between a device object and a device info
object is that device objects are usually 'registered' with a device manager
while device info object might or might not be registered with a device
manager.

A device manager object is a mapping object where keys are unique device
identifier (string) and values are device object. 

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


class DeviceManager(dict):
    # XXX if it's worth it, we could split the 'device management'
    # from the 'search' (search with cache or without cache) and a way
    # to notify the 'searcher' object of change to device manager (observer
    # pattern)
    def __init__(self, id_gen):
        self._id_gen = id_gen
    
    def add(self, dev):
        """Add a new device with an automatically generated id
        to this device manager.
        
        Return the ID of the newly added device.
        
        """
        dev_id = self._id_gen.next()
        self[dev_id] = dev
        return dev_id
    
    def find(self, fun):
        """Return the first device ID for which fun(dev) is true, or None 
        if no such device exist.
        
        """
        for dev_id, dev in self.iteritems():
            if fun(dev):
                return dev_id
        return None
    
    def find_ip(self, ip):
        """Return the first device ID for which dev.get('ip') == ip, or
        None if no such device exist.
        
        This is equivalent to 'find(lambda d: d.get('ip') == ip)' but
        calling this method might be faster.
        
        """
        return self.find(lambda d: d.get('ip') == ip)
    
    def find_mac(self, mac):
        """Return the first device ID for which dev.get('mac') == mac, or
        None if no such device exist.
        
        This is equivalent to 'find(lambda d: d.get('mac') == mac)' but
        calling this method might be faster.
        
        """
        return self.find(lambda d: d.get('mac') == mac)
    
    def filter(self, fun):
        """Yield every device IDs for which fun(dev) is true."""
        for dev_id, dev in self.iteritems():
            if fun(dev):
                yield dev_id
