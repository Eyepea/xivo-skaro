# -*- coding: UTF-8 -*-

"""Plugin for Snom 320 and 820 in version 8.4.18."""

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
from prov2.plugins import Plugin, StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from prov2.util import norm_mac, format_mac
from twisted.internet import defer
from xivo import tzinform


_UA_REGEX = re.compile(r'\bsnom(\d{3})-SIP (\d+\.\d+\.\d+)\b')

def _ua_identifier(user_agent):
    m = _UA_REGEX.search(user_agent)
    if m:
        return {'vendor': 'Snom', 'model': m.group(1), 'version': m.group(2)}

_HTTP_FILENAME_REGEX = re.compile('snom\d{3}-([\dA-F]{12})\b')

def _http_identifier(request):
    # "Mozilla/4.0 (compatible; snom820-SIP 8.4.18 1.1.4-IFX-26.11.09)"
    # "Mozilla/4.0 (compatible; snom320-SIP 8.4.18 1.1.3-s)"
    ua = request.getHeader('User-Agent')
    if ua:
        dev = _ua_identifier(ua)
        if dev:
            m = _HTTP_FILENAME_REGEX.search(request.path)
            if m:
                dev['mac'] = norm_mac(m.group(1))
            return dev


class _HTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        return defer.succeed(_http_identifier(request))


class SnomPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    _ENCODING = 'UTF-8'
    _SNOM_LOCALES = {
        'de_DE': ('Deutsch', 'GER'),
        'en_US': ('English', 'USA'),
        'es_ES': ('Espanol', 'ESP'),
        'fr_FR': ('Francais', 'FRA'),
        'fr_CA': ('Francais', 'USA'),
    }
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, plugin_dir, gen_cfg, spec_cfg)
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('http_proxy'))
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        self.services = self._fetchfw_helper.services()
    
    http_dev_info_extractor = _HTTPDeviceInfoExtractor()
    
    device_types = [('Snom', model, '8.4.18') for model in ('320', '820')]
    
    def configure_common(self, config):
        for tpl_name in ('gui_lang.xml', 'snom320.htm', 'snom320.xml', 'snom320-firmware.xml',
                         'snom820.htm', 'snom820.xml', 'snom820-firmware.xml', 'snom-general.xml',
                         'web_lang.xml'):
            tpl = self._tpl_helper.get_template(tpl_name)
            filename = os.path.join(self._tftpboot_dir, tpl_name)
            self._tpl_helper.dump(tpl, config, filename, self._ENCODING)
    
    @classmethod
    def _format_function_keys(cls, funckey, proxy_ip):
        sorted_keys = funckey.keys()
        sorted_keys.sort()
        fk_config_lines = []
        for key in sorted_keys:
            value = funckey[key]
            exten = value['exten']

            if value.get('supervision'):
                xtype = "dest"
            else:
                xtype = "speed"
            fk_config_lines.append('<fkey idx="%d" context="active" perm="R">%s &lt;sip:%s@%s&gt;</fkey>' % (int(key)-1, xtype, exten, proxy_ip))
        return "\n".join(fk_config_lines)
    
    @classmethod
    def _format_locale(cls, locale):
        return """\
    <language perm="R">%s</language>
    <web_language perm="R">%s</language>
    <tone_scheme perm="R">%s</tone_scheme>""" % (cls._SNOM_LOCALES[locale][0],
                                                 cls._SNOM_LOCALES[locale][0],
                                                 cls._SNOM_LOCALES[locale][1])
    
    @classmethod
    def _format_dst_change(cls, dst_change):
        fmted_time = '%02d:%02d:%02d' % tuple(dst_change['time'].as_hms)
        day = dst_change['day']
        if day.startswith('D'):
            return '%02d.%02d %s' % (int(day[1:]), dst_change['month'], fmted_time)
        else:
            week, weekday = map(int, day[1:].split('.'))
            weekday = tzinform.week_start_on_monday(weekday)
            return '%02d.%02d.%02d %s' % (dst_change['month'], week, weekday, fmted_time)
    
    @classmethod
    def _format_tz_inform(cls, inform):
        lines = []
        lines.append('<timezone perm="R"></timezone>')
        lines.append('<utc_offset perm="R">%+d</utc_offset>' % inform['utcoffset'].as_seconds)
        if inform['dst'] is None:
            lines.append('<dst perm="R"></dst>')
        else:
            lines.append('<dst perm="R">%d %s %s</dst>' % 
                         (inform['dst']['save'].as_seconds,
                          cls._format_dst_change(inform['dst']['start']),
                          cls._format_dst_change(inform['dst']['end'])))
        return '\n'.join(lines)
    
    def configure(self, dev, config):
        model = dev['model']
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        
        try:
            # get device-specific template
            tpl = self._tpl_helper.get_template(fmted_mac + '.xml')
        except TemplateNotFound:
            # get model-specific template
            tpl = self._tpl_helper.get_template('snom-template.xml')
        
        config['XX_function_keys'] = self._format_function_keys(config['funckey'], config['sip'][0]['proxy_ip'])
        config['XX_language'] = self._format_locale(config['locale'])
        config['XX_timezone'] = self._format_tz_inform(tzinform.get_timezone_info(config['timezone']))
        
        redir_filename = os.path.join(self._tftpboot_dir, "snom%s-%s.htm" % (model, fmted_mac))
        redir_file = open(redir_filename, 'w')
        redir_file.write(
"""\
<?xml version="1.0" encoding="UTF-8" ?>
<setting-files>
  <file url="http://%s:%s/snom%s-%s.xml"/>
</setting-files>
""" % (config['prov_ip'], config['prov_http_port'], model, fmted_mac))
        redir_file.close()
        filename = os.path.join(self._tftpboot_dir, "snom%s-%s.xml" % (model, fmted_mac))
        self._tpl_helper.dump(tpl, config, filename, self._ENCODING)
