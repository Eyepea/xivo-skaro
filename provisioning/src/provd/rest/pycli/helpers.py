# -*- coding: UTF-8 -*-

"""Various helpers functions to be used in the CLI."""

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

# importing <module> as _<module> so that import are not autocompleted in the CLI
import operator as _operator


def _init_module(configs, devices, plugins):
    # MUST be called from another module before the function in this module
    # are made available in the CLI
    global _configs
    global _devices
    global _plugins
    _configs = configs
    _devices = devices
    _plugins = plugins


def _itemgetter_default(item, default):
    def aux(obj):
        try:
            return obj[item]
        except KeyError:
            return default
    return aux


def used_plugins():
    """Return a list of plugins used by devices."""
    s = set(map(_itemgetter_default(u'plugin', None), _devices.find(fields=[u'plugin'])))
    # None might be present if at least one device had no plugins
    s.discard(None)
    return sorted(s)


def installed_plugins():
    """Return a list of all installed plugins."""
    return sorted(_plugins.installed().iterkeys())


def unused_plugins():
    """Return the list of unused plugins, i.e. installed plugins that no devices are using."""
    return list(set(installed_plugins()) - set(used_plugins()))


def missing_plugins():
    """Return the list of plugins used by devices that are not installed."""
    return list(set(used_plugins()) - set(installed_plugins()))


def mass_update_devices_plugin(old_plugin, new_plugin, synchronize=False):
    """Update all devices using plugin old_plugin to plugin new_plugin, and
    optionally synchronize the affected devices.
    
    """ 
    if not isinstance(old_plugin, basestring):
        raise ValueError(old_plugin)
    if not isinstance(new_plugin, basestring):
        raise ValueError(new_plugin)
    
    for device in _devices.find({u'plugin': old_plugin}):
        device[u'plugin'] = new_plugin
        print "Updating device %s" % device[u'id']
        _devices.update(device)
        if synchronize:
            print "Synchronizing device %s" % device[u'id']
            _devices.synchronize(device)
        print


def mass_synchronize():
    for device in _devices.find(fields=[u'id']):
        print "Synchronizing device %s" % device[u'id']
        _devices.synchronize(device)
        print


def clean_transient_config():
    """Remove any unused transient config. Mostly useful for debugging purpose."""
    n = 0
    for config in map(_operator.itemgetter('id'), _configs.find({u'transient': True}, fields=['id'])):
        if not _devices.find({u'config': config}, fields=['id']):
            print "Removing config %s" % config
            _configs.remove(config)
            n += 1
    print "%d unused transient configs have been removed" % n
