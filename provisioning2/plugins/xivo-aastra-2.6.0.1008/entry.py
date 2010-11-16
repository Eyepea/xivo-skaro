# -*- coding: UTF-8 -*-

"""Plugin for Aastra 6731i and 6757i in version 2.6.0.1008."""

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
from prov2.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from prov2.util import to_mac, from_mac
from jinja2 import TemplateNotFound
from xivo import tzinform


def _parse_model(model_raw):
    return {'Aastra6731i': '6731i', 'Aastra57i': '6757i'}.get(model_raw)

def _parse_mac(mac_raw):
    if mac_raw.startswith('MAC:'):
        # looks like a valid MAC token..
        try:
            return to_mac(mac_raw[len('MAC:'):])
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
    # UA: "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.1008-SIP"
    ua = request.getHeader('User-Agent')
    if ua:
        return _ua_identifier(ua)


class AastraPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    _ENCODING = 'UTF-8'
    # XXX actually, we didn't find which encoding to use  
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, plugin_dir, gen_cfg, spec_cfg)
        # XXX I think next line could be moved in StandardPlugin
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, gen_cfg.get('http_proxy'))
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
    def services(self):
        return self._fetchfw_helper.services()
    
    def http_dev_info_extractors(self):
        return (_http_identifier,)
    
    def tftp_dev_info_extractors(self):
        # This is not necessary since Aastra are capable of protocol
        # selection inside DHCP option 66 (TFTP server name).
        # That said, there is the rare case where one provisioning
        # server were replaced by this one, and the new one has the
        # same IP address than the old one and the phones were
        # configured to do TFTP and the admin guys are too lazy to
        # configure there DHCP server to change the value of option 66.
        # In this case, this might be useful.
        return ()
    
    def device_types(self):
        return [('Aastra', model, '2.6.0.1008') for model in ('6731i', '6757i')]
    
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
    
    def configure_common(self, config):
        tpl = self._tpl_helper.get_template('aastra.cfg')
        filename = os.path.join(self._tftpboot_dir, 'aastra.cfg')
        self._tpl_helper.dump(tpl, config, filename, self._ENCODING)
    
    def configure(self, dev, config):
        model = dev['model']
        fmted_mac = from_mac(dev['mac'], separator='', uppercase=True)
        
        try:
            # get device-specific template
            tpl = self._tpl_helper.get_template(fmted_mac + '.cfg')
        except TemplateNotFound:
            # get model-specific template
            tpl = self._tpl_helper.get_template(model + '.cfg')
        
        config['XX_function_keys'] = self._format_function_keys(config['funckey'], model)
        config['XX_timezone'] = self._format_tz_inform(tzinform.get_timezone_info(config['timezone']))
        
        filename = os.path.join(self._tftpboot_dir, fmted_mac + '.cfg')
        self._tpl_helper.dump(tpl, config, filename, self._ENCODING)


# XXX DHCP support is temporarily set aside
#
#_VCI_DICT = {
#    'AastraIPPhone6731i': _AASTRA_6731i_ID,
#    'AastraIPPhone6757i': _AASTRA_6757i_ID,
#}
#
#def identify_device_dhcp(request):
#    options = request['options']
#    if VendorClassIdentifierOption in options:
#        vci = options[VendorClassIdentifierOption].value
#        # XXX en fait, on ne connait pas la version exacte, donc ca peut etre un peu
#        # faux ce qui est retourné
#        return _VCI_DICT.get(vci)
#
#
#class DhcpService(object):
#    """Service DHCP du plugin.
#    
#    Ajoute les options specifiques au device lors de requete DHCP.
#    
#    """
#    def __init__(self, config):
#        self._config = config
#    
#    def handle_bootrequest(self, request, response):
#        sname = 'http://%s/' % self._config['http-server-name']
#        response['options'][TFTPServerNameOption] = TFTPServerNameOption(sname)
#        response.commit()

