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


def clean_transient_config():
    n = 0
    for config in map(_operator.itemgetter('id'), _configs.find({u'transient': True}, fields=['id'])):
        if not _devices.find({u'config': config}, fields=['id']):
            print "Removing config %s" % config
            _configs.remove(config)
            n += 1
    print "%d unused transient configs have been removed" % n
