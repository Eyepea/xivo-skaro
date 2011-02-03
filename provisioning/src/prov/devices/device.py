# -*- coding: UTF-8 -*-

"""Device and device collection module.

This module defines 3 kind of objects:
- device info
- device
- device collection

Device info objects and device objects have some similarities. They both
are dictionaries, with the usual restrictions associated with the fact
they may be persisted in a document collection.

They both have the following standardized keys:
  mac -- the normalized MAC address of this device (unicode)
  sn -- the serial number of this device (unicode)
  ip -- the normalized IP address of this device (unicode)
  vendor -- the vendor name of this device (unicode)
  model -- the model name of this device (unicode)
  version -- the version of the software/firmware of this device (unicode)
  XXX since it's theoretically possible for some device to be used with different software,
    and in these cases a 'version' field is not enough to identify which software its
    using, we might want to add another field like 'firmware' or change the semantic and
    the name of the 'version' field to include not only the version but the firmware name/id

Device objects have also the following standardized keys:
  id -- the ID of this device object (unicode) (mandatory)
  plugin -- the ID of the plugin this device is managed by (unicode)
  config -- the ID of the configuration of this device (unicode)
  configured -- a boolean indicating if the device has been successfully
    configured by a plugin. (boolean) (mandatory)

Non-standard keys should begin with 'X_'.

Finally, device collection objects are used as a storage for device objects.

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

from prov.persist.util import ForwardingDocumentCollection


class DeviceCollection(ForwardingDocumentCollection):
    # right now, a device collection is nothing more than a standard
    # collection
    pass
