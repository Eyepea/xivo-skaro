# -*- coding: UTF-8 -*-

"""Common plugin code shared by the the various xivo-cisco-spa plugins.

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

import math
import os.path
import re
from xml.sax.saxutils import escape
from prov2 import sip
from prov2.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    PROBABLE_SUPPORT, COMPLETE_SUPPORT, FULL_SUPPORT
from prov2.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from prov2.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.python import failure
from xivo import tzinform


class BaseCiscoDHCPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'dhcp'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        if 60 in request:
            return self._extract_from_vdi(request[60])
    
    def _extract_from_vdi(self, vdi):
        # Vendor class identifier:
        #   "LINKSYS SPA-942" (6.1.5a)
        #   "LINKSYS SPA-962" (6.1.5a)
        #   "LINKSYS SPA8000" (unknown version)
        #   "Cisco SPA501G" (7.4.4)
        #   "Cisco SPA508G" (7.4.4)
        #   "Cisco SPA525g" (from Cisco doc, unknown version)
        #   "Cisco SPA525G" (7.4.4/7.4.7)
        tokens = vdi.split()
        if len(tokens) == 2:
            raw_vendor, raw_model = tokens
            if raw_vendor in ('LINKSYS', 'Cisco'):
                dev_info = {'vendor': 'Cisco'}
                dev_info['model'] = raw_model.replace('-', '').uppercase()


class BaseCiscoHTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_from_ua(ua, dev_info)
            if dev_info:
                dev_info['vendor'] = 'Cisco'
                return dev_info
    
    def _extract_from_ua(self, ua, dev_info):
        # HTTP User-Agent:
        # Note: the last group of digit is the serial number;
        #       the first, if present, is the MAC address
        #   "Linksys/SPA-942-6.1.5(a) (88019FA42805)"
        #   "Linksys/SPA-962-6.1.5(a) (4MM00F903042)"
        #   "Cisco/SPA501G-7.4.4 (8843E157DDCC)(CBT141100HR)"
        #   "Cisco/SPA508G-7.4.4 (0002FDFF2103)(CBT141400UK)"
        #   "Cisco/SPA525G-7.4.4 (CBT141900G7)"
        #   "Cisco/SPA525G-7.4.7 (CBT141900G7)"
        if ua.startswith('Linksys/'):
            self._extract_linksys_from_ua(ua, dev_info)
        elif ua.startswith('Cisco/'):
            self._extract_cisco_from_ua(ua, dev_info)
    
    _LINKSYS_UA_REGEX = re.compile(r'^Linksys/([\w\-]+)-([^\s\-]+) \((\w+)\)$')
    
    def _extract_linksys_from_ua(self, ua, dev_info):
        # Pre: ua.startswith('Linksys/')
        m = self._LINKSYS_UA_REGEX.match(ua)
        if m:
            raw_model, version, sn = m.groups()
            dev_info['model'] = raw_model.replace('-', '')
            dev_info['version'] = version
            dev_info['sn'] = sn
    
    _CISCO_UA_REGEX = re.compile(r'^Cisco/(\w+)-(\S+) (?:\(([\dA-F]{12})\))?\((\w+)\)$')
    
    def _extract_cisco_from_ua(self, ua, dev_info):
        # Pre: ua.startswith('Cisco/')
        m = self._CISCO_UA_REGEX.match(ua)
        if m:
            model, version, raw_mac, sn = m.groups()
            dev_info['model'] = model
            dev_info['version'] = version
            if raw_mac:
                dev_info['mac'] = norm_mac(raw_mac)
            dev_info['sn'] = sn


class BaseCiscoTFTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'tftp'
        return defer.succeed(self._do_extract(request))
    
    _SEPFILE_REGEX = re.compile(r'^SEP([\dA-F]{12})\.cnf\.xml$'), 
    _SPAFILE_REGEX = re.compile(r'^/spa(.+?)\.cfg$')
    
    def _test_sepfile(self, filename):
        # Test if filename is "SEPMAC.cnf.xml".
        m = self._SEPFILE_REGEX.match(filename)
        if m:
            return {'mac': norm_mac(m.group(1))}
    
    def _test_spafile(self, filename):
        # Test if filename is "/spa$PSN.cfg".
        m = self._SPAFILE_REGEX.match(filename)
        if m:
            return {'model': 'SPA' + m.group(1).upper()}
    
    def _test_init(self, filename):
        # Test if filename is "/init.cfg".
        if filename == '/init.cfg':
            return {'model': 'PAP2T'}
    
    _TEST_CHAIN = [_test_sepfile, _test_spafile, _test_init]
    
    def _do_extract(self, request):
        packet = request['packet']
        filename = packet['filename']
        for test_fun in self._TEST_CHAIN:
            dev_info = test_fun(filename)
            if dev_info:
                dev_info['vendor'] = 'Cisco'
                return dev_info


class BaseCiscoPgAssociator(BasePgAssociator):
    def __init__(self, model_version):
        BasePgAssociator.__init__(self)
        self._model_version = model_version
    
    def _do_associate(self, vendor, model, version):
        if vendor == 'Cisco':
            if model in self._model_version:
                if version == self._model_version[model]:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            if model is not None:
                # model is unknown to the plugin, chance are low
                # that's it's going to be supported because of missing
                # common configuration file that are used to bootstrap
                # the provisioning process
                return IMPROBABLE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseCiscoPlugin(StandardPlugin):
    """Base classes MUST have an '_COMMON_FILENAMES' attribute which is a
    sequence of filenames that will be generated by the common template in
    the common_configure function.
    
    """
    
    _ENCODING = 'UTF-8'
    _XX_LANG = {
        'de_DE': 'German',
        'en_US': 'English',
        'es_ES': 'Spanish',
        'fr_FR': 'French',
        'fr_CA': 'French',
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('http_proxy'))
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        self.services = self._fetchfw_helper.services() 
    
    dhcp_dev_info_extractor = BaseCiscoDHCPDeviceInfoExtractor()
    
    http_dev_info_extractor = BaseCiscoHTTPDeviceInfoExtractor()
    
    tftp_dev_info_extractor = BaseCiscoTFTPDeviceInfoExtractor()
    
    def configure_common(self, config):
        tpl = self._tpl_helper.get_template('common/model.cfg.tpl')
        common_filenames = self._COMMON_FILENAMES
        for filename in common_filenames:
            dst = os.path.join(self._tftpboot_dir, filename)
            self._tpl_helper.dump(tpl, config, dst, self._ENCODING)
    
    def _format_function_keys_unit(self, key, func):
        unit = int(math.ceil(float(key) / 32))
        key %= 32

        if key == 0:
            key = 32

        return '<Unit_%d_Key_%d>%s</Unit_%d_Key_%d>' % (unit, key, func, unit, key)
    
    def _format_function_keys(self, funckey, model):
        if model is None:
            return ''
        sorted_keys = funckey.keys()
        sorted_keys.sort()
        fk_config_lines = []
        for key in sorted_keys:
            value   = funckey[key]
            exten   = value['exten']
            key     = int(key)
            if 'label' in value and value['label'] is not None:
                label = value['label']
            else:
                label = exten
            label = escape(label)

            if value.get('supervision'):
                blf = "+blf"
            else:
                blf = ""

            func = "fnc=sd+cp%s;sub=%s@$PROXY;nme=%s" % (blf, exten, label)

            if model in ('SPA501G', 'SPA508G'):
                if key > 8:
                    key -= 8
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == 'SPA502G':
                if key > 2:
                    key -= 2
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == 'SPA504G':
                if key > 4:
                    key -= 4
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == 'SPA509G':
                if key > 12:
                    key -= 12
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == 'SPA525G':
                if key > 5:
                    key -= 5
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif key > 12:
                continue

            fk_config_lines.append('<Short_Name_%d_>%s</Short_Name_%d_>' % (key, label, key))
            fk_config_lines.append('<Extended_Function_%d_>%s</Extended_Function_%d_>' % (key, func, key))
        return "\n".join(fk_config_lines)
    
    def _get_xx_fkeys(self, config, model):
        if 'funckey' in config:
            return self._format_function_keys(config['funckey'], model)
    
    def _format_dst_change(self, dst_change):
        _day = dst_change['day']
        if _day.startswith('D'):
            day = _day[1:]
            weekday = '0'
        else:
            week, weekday = _day[1:].split('.')
            weekday = tzinform.week_start_on_monday(int(weekday))
            if week == '5':
                day = '-1'
            else:
                day = (int(week) - 1) * 7 + 1
        
        h, m, s = dst_change['time'].as_hms
        return ('%s/%s/%s/%s:%s:%s' %
                (dst_change['month'], day, weekday, h, m, s))
    
    def _format_tz_inform(self, inform):
        lines = []
        hours, minutes = inform['utcoffset'].as_hms[:2]
        lines.append('<Time_Zone>GMT%+03d:%02d</Time_Zone>' % (hours, minutes))
        # We need to substract 1 from the computed hour (bug in the SPA firmware?)
        # In fact, this might be caused by a DHCP Time Offset option
        lines.append('<Time_Offset__HH_mm_>%d/%d</Time_Offset__HH_mm_>' % (hours - 1, minutes))
        if inform['dst'] is None:
            lines.append('<Daylight_Saving_Time_Enable>no</Daylight_Saving_Time_Enable>')
        else:
            lines.append('<Daylight_Saving_Time_Enable>yes</Daylight_Saving_Time_Enable>')
            h, m, s = inform['dst']['save'].as_hms
            lines.append('<Daylight_Saving_Time_Rule>start=%s;end=%s;save=%d:%d:%s</Daylight_Saving_Time_Rule>' %
                         (self._format_dst_change(inform['dst']['start']),
                          self._format_dst_change(inform['dst']['end']),
                          h, m, s,
                          ))
        return '\n'.join(lines)
    
    def _get_xx_timezone(self, config):
        if 'timezone' in config:
            return self._format_tz_inform(tzinform.get_timezone_info(config['timezone']))
    
    def _format_proxy(self, line):
        proxy_value = 'xivo_proxies:SRV=%s:5060:p=0' % line['proxy_ip']
        if 'backup_proxy_ip' in line:
            proxy_value += '|%s:5060:p=1' % line['backup_proxy_ip']
        return proxy_value
    
    def _get_xx_proxies(self, config):
        proxies = {}
        for line_no, line in config['sip']['lines'].iteritems():
            proxies[line_no] = self._format_proxy(line)
        return proxies
    
    def _get_xx_language(self, config):
        if 'locale' in config:
            return self._XX_LANG.get(config['locale'])
        
    def _dev_specific_filename(self, dev):
        """Return the filename of the device specific configuration file of
        device dev.
        
        """
        fmted_mac = format_mac(dev['mac'], separator='')
        return fmted_mac + '.xml'
    
    def configure(self, dev, config):
        filename = self._dev_specific_filename(dev)
        tpl = self._tpl_helper.get_dev_template(filename, dev)
        
        config['XX_fkeys'] = self._get_xx_fkeys(config, dev.get('model'))
        config['XX_timezone'] = self._get_xx_timezone(config)
        config['XX_proxies'] = self._get_xx_proxies(config)
        config['XX_language'] = self._get_xx_language(config)
        
        dst = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, config, dst, self._ENCODING)
    
    def deconfigure(self, device):
        filename = self._dev_specific_filename(device)
        try:
            os.remove(filename)
        except OSError:
            # ignore -- probably an already removed file
            pass
    
    def synchronize(self, device, raw_config):
        try:
            ip = device[u'ip']
        except KeyError:
            return defer.fail(Exception('no IP address'))
        else:
            def on_notify_success(status_code):
                if status_code == 200:
                    return None
                else:
                    e = Exception('SIP NOTIFY failed with status "%s"' % status_code)
                    return failure.Failure(e)
            
            for sip_line in raw_config[u'sip'][u'lines'].itervalues():
                username = sip_line[u'user_id']
                password = sip_line[u'passwd']
                break
            else:
                e = Exception('Need at least one configured line to resynchronize')
                return failure.Failure(e)
            uri = sip.URI('sip', ip, user=username, port=5060)
            d = sip.send_notify(uri, 'check-sync', (username, password))
            d.addCallback(on_notify_success)
            return d
