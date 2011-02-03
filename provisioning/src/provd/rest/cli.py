# -*- coding: UTF-8 -*-

"""A small CLI to manage the provisioning server."""

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

import cmd
from pprint import pprint
from provd.rest.client import RestClientService


class Cli(cmd.Cmd):
    # Command names are not like we would like them to be because of
    # the restrictions imposed by Cmd. We would like our command to
    # be a bit more 'hierarchical', like those in asterisk.
    
    prompt = 'prov> '
    
    def __init__(self, service):
        cmd.Cmd.__init__(self)
        self._service = service
    
    def emptyline(self):
        return
        
    def do_EOF(self, line):
        print
        return True
    
    def do_devadd(self, line):
        """devadd [<key> <value>] ...
        Add a device to the provisioner server.
        
        devadd ip 192.168.32.254 mac 001122334455 vendor aastra model snom version 8.4.18"""
        tokens = line.split()
        if len(tokens) % 2 == 1:
            # odd number of tokens
            print 'Invalid number of tokens'
            return
        req_dev = dict((tokens[i], tokens[i + 1]) for i in xrange(0, len(tokens), 2))
        dev_id, resp_dev = self._service.add_dev(req_dev)
        print "Device added"
        print dev_id, str(resp_dev)
        
    def do_devrm(self, line):
        """devrm <dev_id>
        Remove a device."""
        dev_id = line
        if self._service.remove_dev(dev_id):
            print "Device removed."
        else:
            print "No device found."
    
    def do_devget(self, line):
        """devget <dev_id>
        Get a device."""
        dev_id = line
        dev = self._service.get_dev(dev_id)
        if dev is None:
            print "No device found."
        else:
            pprint(dev)
    
    def do_devset(self, line):
        tokens = line.split()
        dev_id = tokens.pop(0)
        if len(tokens) % 2 == 1:
            # odd number of tokens
            print 'Invalid number of tokens'
            return
        dev = dict((tokens[i], tokens[i + 1]) for i in xrange(0, len(tokens), 2))
        if self._service.set_dev(dev_id, dev):
            print "Device setted."
        else:
            print "No device found."
    
    def do_devconf(self, line):
        """devconf <dev_id>
        Reconfigure a device."""
        dev_id = line
        if self._service.reconfigure_dev(dev_id):
            print "Device reconfigured"
        else:
            print "Error while reconfiguring (does the device exist?)"
            
    def do_devreload(self, line):
        """devconf <dev_id>
        Reload a device."""
        dev_id = line
        if self._service.reload_dev(dev_id):
            print "Device reloaded"
        else:
            print "Error while reloading (does the device exist?)"
    
    def do_devlist(self, line):
        """devlist
        List the devices managed by the provisioning server."""
        for dev_id, dev in self._service.list_dev():
            print dev_id, str(dev)
            
    def do_cfglist(self, line):
        """cfglist
        List the config IDs managed by the provisioning server."""
        for cfg_id in self._service.list_cfg():
            print cfg_id
    
    def do_cfggeti(self, line):
        """cfggeti <cfg_id>
        Get a config in 'individual format'."""
        cfg_id = line
        res = self._service.get_cfgi(cfg_id)
        if res is None:
            print "No config found."
        else:
            cfg, cfg_base_ids = res
            print "Config '%s' inherits from %s" % (cfg_id, cfg_base_ids)
            pprint(cfg)
    
    def do_cfggetc(self, line):
        """cfggetc <cfg_id>
        Get a config in 'composite format'."""
        cfg_id = line
        cfg = self._service.get_cfgc(cfg_id)
        if cfg is None:
            print "No config found."
        else:
            pprint(cfg)
            
    def do_cfgrm(self, line):
        """cfgrm <cfg_id>
        Remove a config."""
        cfg_id = line
        res = self._service.remove_cfg(cfg_id)
        if res:
            print "Config removed."
        else:
            print "No config found."

    def do_cfgset(self, line):
        """cfgsetc <cfg_id> [-base <base>] [<key> <value>] ...
        Update/create a config."""
        # XXX support only one base config for now, we'll want to support more
        #     but we need to find out a syntax that make sense for it
        # TODO we could try reading the line as json/python expression, so that
        #      the user can specify complex stuff, etc
        tokens = line.split()
        cfg_id = tokens.pop(0)
        if len(tokens) % 2 == 1:
            # odd number of tokens
            print 'Invalid number of tokens'
            return
        startidx = 0
        cfg_base_ids = []
        if tokens[0] == '-base':
            startidx = 2
            cfg_base_ids.append(tokens[1])
        cfg = dict((tokens[i], tokens[i + 1]) for i in xrange(startidx, len(tokens), 2))
        if self._service.set_cfg(cfg_id, cfg, cfg_base_ids):
            print "Config setted."
        else:
            print "No device found." 
        

if __name__ == '__main__':
    import sys
    try:
        base_url = sys.argv[1]
    except IndexError:
        base_url = 'http://127.0.0.1:8081/'
    
    Cli(RestClientService(base_url)).cmdloop()
