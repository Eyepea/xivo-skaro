# -*- coding: UTF-8 -*-

__author__ = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import logging, subprocess, traceback

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW, CMD_R
from xivo_sysconf import jsoncore


class CommonConf(jsoncore.JsonCore):
    def __init__(self):
        super(CommonConf, self).__init__()
        self.log = logging.getLogger('xivo_sysconf.modules.commonconf')

        http_json_server.register(self.generate , CMD_RW,
            safe_init=self.safe_init,
            name='commonconf_generate')
        http_json_server.register(self.apply, CMD_R, name='commonconf_apply')

    def enable_disable_dhcpd(self, args):
        if 'xivo.dhcp.active' in args:
            if args['xivo.dhcp.active']:
                cmd = ['ln',
                      '-s',
                      '%s/isc-dhcp-server' % self.monit_checks_dir,
                      '%s/isc-dhcp-server' % self.monit_conf_dir]
            else:
                cmd = ['rm', '-f', '%s/isc-dhcp-server' % self.monit_conf_dir]
            try:
                p = subprocess.Popen(cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     close_fds=True)
                ret = p.wait()
                output = p.stdout.read()
            except OSError:
                traceback.print_exc()
                raise HttpReqError(500, "can't apply ha changes")

    def generate(self, args, options):
        self.enable_disable_dhcpd(args)
        super(CommonConf, self).generate(args, options)

    def safe_init(self, options):
        super(CommonConf, self).safe_init(options)

        self.file = options.configuration.get('commonconf', 'commonconf_file')
        self.cmd = options.configuration.get('commonconf', 'commonconf_cmd')
        self.monit = options.configuration.get('commonconf', 'commonconf_monit')
        self.monit_checks_dir = options.configuration.get('monit', 'monit_checks_dir')
        self.monit_conf_dir = options.configuration.get('monit', 'monit_conf_dir')

    SECTIONS = {
        '1. VoIP'       : ['xivo.voip.ifaces'],
        '2. Network'    : [
            'xivo.hostname', 'xivo.domain', 'xivo.net4.ip',
            'xivo.net4.netmask', 'xivo.net4.broadcast', 'xivo.net4.subnet',
            'xivo.extra.dns.search', 'xivo.nameservers'
         ],
        '3. DHCP'       : [
            'xivo.dhcp.active', 'xivo.dhcp.pool', 'xivo.dhcp.extra_ifaces'
         ],
        '4. Mail'       : [
            'xivo.smtp.mydomain', 'xivo.smtp.origin', 'xivo.smtp.relayhost',
            'xivo.smtp.fallback_relayhost', 'xivo.smtp.canonical'
         ],
        '5. Provd'      : [
            'xivo.provd.net4_ip',
            'xivo.provd.http_port',
            'xivo.provd.dhcp_integration',
            'xivo.provd.rest_net4_ip',
            'xivo.provd.rest_port',
            'xivo.provd.rest_authentication',
            'xivo.provd.rest_ssl',
            'xivo.provd.username',
            'xivo.provd.password'
         ],
        '6. Maintenance': ['xivo.maintenance'],
        '7. Alerts'     : ['alert_emails', 'dahdi_monitor_ports', 'max_call_duration'],
        '8. Databases'  : ['xivo.xivodb' , 'xivo.astdb']
    }
    KEYSELECT = ''
    
    ## overriden generators
    def _gen_bool(self, f, key, value):
        value = 1 if value else 0
        f.write("%s=%d\n" % (key, value))
    ## /

    def apply(self, args, options):
        ret = -1
        try:
            p = subprocess.Popen([self.cmd], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
            ret = p.wait()
            output = p.stdout.read()
            self.log.debug("commonconf apply: %d" % ret)

            if ret != 0:
                raise HttpReqError(500, output)

            # monit configuration also need to be updated (if emails changed)
            p = subprocess.Popen([self.monit], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 close_fds=True)
            ret = p.wait()
            output += '\n' + p.stdout.read()
            self.log.debug("monit apply: %d" % ret)

            if ret != 0:
                raise HttpReqError(500, output)
        except OSError:
            traceback.print_exc()
            raise HttpReqError(500, "can't apply ha changes")

        return output
        
commonconf = CommonConf()
