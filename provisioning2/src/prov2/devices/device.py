# -*- coding: UTF-8 -*-

"""Device-related stuff module...

A device info object is a mapping object with the following keys:
  mac -- the MAC address of this device (6-bytes string) 
  ip -- the (last seen) IP address of this device (4-bytes string)
  vendor -- the vendor name of this device (string)
  model -- the model name of this device (string)
  version -- the version of the software/firmware of this device (string)
XXX  class -- the class of this device ? not sure that's useful

A device object is a device info object + the followings keys:
  plugin -- the name of the plugin this device is managed by (string)
  config -- the name of the configuration of this device (string)

The most meaningful difference between a device object and a device info
object is that device objects are usually 'registered' with a device manager
while device info object might or might not be registered with a device
manager.

XXX experimental, might have no value
A device class object is a mapping object with the following keys:
  id -- the identifier of the class

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

class DeviceManager(object):
    """An object that manages device objects."""
    
    def __init__(self):
        # a list since we haven't decided yet if the 'mac' item of device objects
        # is mandatory or not...
        self._devices = []
    
#    XXX might not be a good idea -- too heavy/complex
#    def ip_view(self):
#        pass
#    
#    def mac_view(self):
#        pass

    def contains_ip(self, ip):
        try:
            self.get_by_ip(ip)
        except KeyError:
            return False
        else:
            return True

    def contains_mac(self, mac):
        try:
            self.get_by_mac(mac)
        except KeyError:
            return False
        else:
            return True

    def get_by_ip(self, ip):
        return self._get_by('ip', ip)
    
    def get_by_mac(self, mac):
        return self._get_by('mac', mac)
        
    def _get_by(self, key, value):
        for device in self._devices:
            if device.get(key) == value:
                return device
        else:
            raise KeyError(value)
        
    def add_device(self, dev):
        if 'mac' in dev and self.contains_mac(dev['mac']):
            raise ValueError('device already exist -- MAC')
        if 'ip' in dev and self.contains_ip(dev['ip']):
            raise ValueError('device already exist -- IP')
        self._devices.append(dev)
    
    def _del_by(self, key, value):
        for i in xrange(len(self._devices)):
            if self._devices[i].get(key) == value:
                del self._devices[i]
                return
        else:
            raise KeyError(value)
    
    def del_device(self, dev):
        if 'mac' in dev and self.contains_mac(dev['mac']):
            self._del_by('mac', dev['mac'])
        elif 'ip' in dev and self.contains_ip('ip'):
            self._del_by('ip', dev['ip'])
        else:
            raise ValueError('no device to delete')
