# -*- coding: UTF-8 -*-

"""Plugin for Aastra 6731i and 6757i in version 2.6.0.

# TODO we should probably specify...
#     ...in which version this plugin will upgrade the device (version 2.6.0.2010 right now)
#     ...which devices this plugin will probably support (Aastra <model>+94xxi in version 2.x.x)
#     ...which devices this plugin can identify, and how
#     ...which config parameter the plugin use, and how

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

import os.path
import re
from jinja2 import TemplateNotFound
from prov2.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from prov2.util import norm_mac, format_mac
from twisted.internet import defer
from xivo import tzinform


def _parse_model(model_raw):
    return {'Aastra6731i': '6731i', 'Aastra57i': '6757i'}.get(model_raw)

def _parse_mac(mac_raw):
    if mac_raw.startswith('MAC:'):
        # looks like a valid MAC token..
        try:
            return norm_mac(mac_raw[len('MAC:'):])
        except ValueError:
            return

_VERSION_REGEX = re.compile(r'^2\.\d\.\d\.\d+$')
# The expression is 'relaxed' such that we can identify a broader range
# of potentially compatible device

def _parse_version(version_raw):
    if version_raw.startswith('V:') and version_raw.endswith('-SIP'):
        # looks like a valid version token...
        version = version_raw[len('V:'):-len('-SIP')]
        if _VERSION_REGEX.match(version):
            return version

def _ua_identifier(user_agent):
    tokens = user_agent.split()
    if len(tokens) == 3:
        model_raw, mac_raw, v_raw = tokens
        model = _parse_model(model_raw)
        if model:
            dev = {'vendor': 'Aastra', 'model': model}
            mac = _parse_mac(mac_raw)
            if mac:
                dev['mac'] = mac
            version = _parse_version(v_raw)
            if version:
                dev['version'] = version
            return dev


def _http_identifier(request):
    # UA: "Aastra57i MAC:00-08-5D-19-E4-01 V:2.6.0.1008-SIP"
    # UA: "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.2010-SIP"
    # UA: "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.1008-SIP"
    ua = request.getHeader('User-Agent')
    if ua:
        return _ua_identifier(ua)
    

class _HTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        return defer.succeed(_http_identifier(request))


class AastraPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    _ENCODING = 'UTF-8'
    # XXX actually, we didn't find which encoding to use  
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, plugin_dir, gen_cfg, spec_cfg)
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('http_proxy'))
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        self.services = self._fetchfw_helper.services() 
        
    http_dev_info_extractor = _HTTPDeviceInfoExtractor()
    
    tftp_dev_info_extractor = None
    # This is not necessary since Aastra are capable of protocol
    # selection inside DHCP option 66 (TFTP server name).
    # That said, there is the rare case where one provisioning
    # server were replaced by this one, and the new one has the
    # same IP address than the old one and the phones were
    # configured to do TFTP and the admin guys are too lazy to
    # configure there DHCP server to change the value of option 66.
    # In this case, this might be useful.
    
    device_types = [('Aastra', model, version) for
                    model in ('6731i', '6757i') for
                    version in ('2.6.0.1008', '2.6.0.2010')]
    
    @classmethod
    def _format_expmod(cls, keynum):
        # XXX you get a weird behavior if you have more than 1 M670i expansion module.
        # For example, if you have a 6757i and you want to set the first key of the
        # second module, you'll have to pick, in the xivo web interface, the key number
        # 91 (30 phone softkeys + 60 M675i expansion module keys + 1) instead of 67.
        # That's because the Aastras support more than one type of expansion module, and they
        # don't have the same number of keys. Since we don't know which one the phone is actually
        # using, we pick the one with the most keys, so every expansion module can be fully
        # used, but this leave a weird behavior for multi-expansion setup when smaller
        # expansion module are used....
        if keynum <= 180:
            return "expmod%d key%d" % ((keynum - 1) // 60 + 1, (keynum - 1) % 60 + 1)
        return None
    
    @classmethod
    def _get_keytype_from_model_and_keynum(cls, model, keynum):
        if model in ("6730i", "6731i"):
            if keynum <= 8:
                return "prgkey%d" % keynum
        elif model in ("6739i"):
            if keynum <= 55:
                return "softkey%d" % keynum
            else:
                return cls._format_expmod(keynum - 55)
        elif model in ("6753i"):
            if keynum <= 6:
                return "prgkey%d" % keynum
            else:
                return cls._format_expmod(keynum - 6)
        elif model in ("6755i"):
            if keynum <= 6:
                return "prgkey%d" % keynum
            else:
                keynum -= 6
                if keynum <= 6:
                    return "softkey%d" % keynum
                else:
                    return cls._format_expmod(keynum - 6)
        elif model in ("6757i"):
            # The 57i has 6 'top keys' and 6 'bottom keys'. 10 functions are programmable for
            # the top keys and 20 are for the bottom keys.
            if keynum <= 10:
                return "topsoftkey%d" % keynum
            else:
                keynum -= 10
                if keynum <= 20:
                    return "softkey%d" % keynum
                else:
                    return cls._format_expmod(keynum - 20)
        return None
    
    @classmethod
    def _format_function_keys(cls, funckey, model):
        sorted_keys = funckey.keys()
        sorted_keys.sort()
        fk_config_lines = []
        for key in sorted_keys:
            keytype = cls._get_keytype_from_model_and_keynum(model, int(key))
            if keytype is not None:
                value = funckey[key]
                exten = value['exten']
                if value.get('supervision'):
                    xtype = "blf"
                else:
                    xtype = "speeddial"
                if 'label' in value and value['label'] is not None:
                    label = value['label']
                else:
                    label = exten
                fk_config_lines.append("%s type: %s" % (keytype, xtype))
                fk_config_lines.append("%s label: %s" % (keytype, label))
                fk_config_lines.append("%s value: %s" % (keytype, exten))
                fk_config_lines.append("%s line: 1" % (keytype,))
        return "\n".join(fk_config_lines)
    
    @classmethod
    def _format_dst_change(cls, suffix, dst_change):
        lines = []
        lines.append('dst %s month: %d' % (suffix, dst_change['month']))
        lines.append('dst %s hour: %d' % (suffix, min(dst_change['time'].as_hours, 23)))
        if dst_change['day'].startswith('D'):
            lines.append('dst %s day: %s' % (suffix, dst_change['day'][1:]))
        else:
            week, weekday = dst_change['day'][1:].split('.')
            if week == '5':
                lines.append('dst %s week: -1' % suffix)
            else:
                lines.append('dst %s week: %s' % (suffix, week))
            lines.append('dst %s day: %s' % (suffix, weekday))
        return lines
    
    @classmethod
    def _format_tz_inform(cls, inform):
        lines = []
        lines.append('time zone name: Custom')
        lines.append('time zone minutes: %d' % -(inform['utcoffset'].as_minutes))
        if inform['dst'] is None:
            lines.append('dst config: 0')
        else:
            lines.append('dst config: 3')
            lines.append('dst minutes: %d' % (min(inform['dst']['save'].as_minutes, 60)))
            if inform['dst']['start']['day'].startswith('D'):
                lines.append('dst [start|end] relative date: 0')
            else:
                lines.append('dst [start|end] relative date: 1')
            lines.extend(cls._format_dst_change('start', inform['dst']['start']))
            lines.extend(cls._format_dst_change('end', inform['dst']['end']))
        return '\n'.join(lines)
    
    def _dev_specific_filename(self, dev):
        """Return the filename of the device specific configuration file of
        device dev."""
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        return os.path.join(self._tftpboot_dir, fmted_mac + '.cfg')
    
    def configure(self, dev, config):
        model = dev['model']
        filename = self._dev_specific_filename(dev)
        
        try:
            # get device-specific template
            tpl = self._tpl_helper.get_template(filename)
        except TemplateNotFound:
            # get model-specific template
            tpl = self._tpl_helper.get_template(model + '.cfg')
        
        config['XX_function_keys'] = self._format_function_keys(config['funckey'], model)
        config['XX_timezone'] = self._format_tz_inform(tzinform.get_timezone_info(config['timezone']))
        
        self._tpl_helper.dump(tpl, config, filename, self._ENCODING)
        
    def deconfigure(self, dev):
        filename = self._dev_specific_filename(dev)
        # Next line should never raise an error if the plugin contract has
        # been followed
        os.remove(filename)

    def reload(self, dev, config):
        # FIXME this is a test, hardcoded value are meaningless outside of my test env
        ip = dev['ip']
        import subprocess
        p = subprocess.Popen(['sip-options',
                              '-m', 'sip:192.168.33.1:5061',
                              '--method=NOTIFY',
                              '--extra',
                              'sip:%s' % ip], stdin=subprocess.PIPE)
        p.communicate('Event: check-sync')
        return defer.succeed(None)
