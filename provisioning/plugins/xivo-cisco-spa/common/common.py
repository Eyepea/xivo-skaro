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

# TODO extract MAC address in the HTTP device info extractor

import math
import os.path
import re
from xml.sax.saxutils import escape
from provd import sip, tzinform
from provd.devices.config import RawConfigError
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    PROBABLE_SUPPORT, COMPLETE_SUPPORT, FULL_SUPPORT
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.servers.http import HTTPNoListingFileService
from provd.servers.tftp.service import TFTPFileService
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.python import failure


def _norm_model(raw_model):
    # Normalize a model name and return it as a unicode string. This removes
    # minus sign and make all the characters uppercase.
    return raw_model.replace('-', '').upper().decode('ascii')


class BaseCiscoDHCPDeviceInfoExtractor(object):
    _RAW_VENDORS = ['LINKSYS', 'Cisco']
    
    def extract(self, request, request_type):
        assert request_type == 'dhcp'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        options = request[u'options']
        if 60 in options:
            return self._extract_from_vdi(options[60])
        return None
    
    def _extract_from_vdi(self, vdi):
        # Vendor class identifier:
        #   "LINKSYS SPA-942" (SPA942 6.1.5a)
        #   "LINKSYS SPA-962" (SPA962 6.1.5a)
        #   "LINKSYS SPA8000" (SPA8000 unknown version)
        #   "Cisco SPA501G" (SPA501G 7.4.4)
        #   "Cisco SPA508G" (SPA508G 7.4.4)
        #   "Cisco SPA525g" (SPA525G unknown version, from Cisco documentation)
        #   "Cisco SPA525G" (SPA525G 7.4.4)
        #   "Cisco SPA525G" (SPA525G 7.4.7)
        #   "Cisco SPA525G2" (SPA525G2 7.4.5)
        tokens = vdi.split()
        if len(tokens) == 2:
            raw_vendor, raw_model = tokens
            if raw_vendor in self._RAW_VENDORS:
                dev_info = {u'vendor': u'Cisco',
                            u'model': _norm_model(raw_model)}
                return dev_info
        return None


class BaseCiscoHTTPDeviceInfoExtractor(object):
    _LINKSYS_UA_REGEX = re.compile(r'^Linksys/([\w\-]+)-([^\s\-]+) \((\w+)\)$')
    _CISCO_UA_REGEX = re.compile(r'^Cisco/(\w+)-(\S+) (?:\(([\dA-F]{12})\))?\((\w+)\)$')
    
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_from_ua(ua, dev_info)
            if dev_info:
                dev_info[u'vendor'] = u'Cisco'
                return dev_info
        return None
    
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
    
    def _extract_linksys_from_ua(self, ua, dev_info):
        # Pre: ua.startswith('Linksys/')
        m = self._LINKSYS_UA_REGEX.match(ua)
        if m:
            raw_model, version, sn = m.groups()
            dev_info[u'model'] = _norm_model(raw_model)
            dev_info[u'version'] = version.decode('ascii')
            dev_info[u'sn'] = sn.decode('ascii')
    
    def _extract_cisco_from_ua(self, ua, dev_info):
        # Pre: ua.startswith('Cisco/')
        m = self._CISCO_UA_REGEX.match(ua)
        if m:
            model, version, raw_mac, sn = m.groups()
            dev_info[u'model'] = model.decode('ascii')
            dev_info[u'version'] = version.decode('ascii')
            if raw_mac:
                dev_info[u'mac'] = norm_mac(raw_mac.decode('ascii'))
            dev_info[u'sn'] = sn.decode('ascii')


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
            raw_mac = m.group(1)
            return {u'mac': norm_mac(raw_mac.decode('ascii'))}
        return None
    
    def _test_spafile(self, filename):
        # Test if filename is "/spa$PSN.cfg".
        m = self._SPAFILE_REGEX.match(filename)
        if m:
            raw_model = 'SPA' + m.group(1)
            return {u'model': _norm_model(raw_model)}
        return None
    
    def _test_init(self, filename):
        # Test if filename is "/init.cfg".
        if filename == '/init.cfg':
            return {u'model': u'PAP2T'}
        return None
    
    _TEST_CHAIN = [_test_sepfile, _test_spafile, _test_init]
    
    def _do_extract(self, request):
        packet = request['packet']
        filename = packet['filename']
        for test_fun in self._TEST_CHAIN:
            dev_info = test_fun(filename)
            if dev_info:
                dev_info[u'vendor'] = u'Cisco'
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
    _XX_LANGUAGE = {
        u'de_DE': u'German',
        u'en_US': u'English',
        u'es_ES': u'Spanish',
        u'fr_FR': u'French',
        u'fr_CA': u'French',
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self.services = fetchfw_helper.services()
        
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
        self.tftp_service = TFTPFileService(self._tftpboot_dir)
    
    dhcp_dev_info_extractor = BaseCiscoDHCPDeviceInfoExtractor()
    
    http_dev_info_extractor = BaseCiscoHTTPDeviceInfoExtractor()
    
    tftp_dev_info_extractor = BaseCiscoTFTPDeviceInfoExtractor()
    
    def configure_common(self, raw_config):
        tpl = self._tpl_helper.get_template('common/model.cfg.tpl')
        common_filenames = self._COMMON_FILENAMES
        for filename in common_filenames:
            dst = os.path.join(self._tftpboot_dir, filename)
            self._tpl_helper.dump(tpl, raw_config, dst, self._ENCODING)
    
    def _format_function_keys_unit(self, key, func):
        unit = int(math.ceil(float(key) / 32))
        key %= 32

        if key == 0:
            key = 32

        return u'<Unit_%d_Key_%d>%s</Unit_%d_Key_%d>' % (unit, key, func, unit, key)
    
    def _format_function_keys(self, funckeys, model):
        if model is None:
            return ''
        sorted_keys = funckeys.keys()
        sorted_keys.sort()
        fk_config_lines = []
        for key in sorted_keys:
            value   = funckeys[key]
            exten   = value[u'exten']
            key     = int(key)
            if u'label' in value and value[u'label'] is not None:
                label = value[u'label']
            else:
                label = exten
            label = escape(label)

            if value.get('supervision'):
                blf = u'+blf'
            else:
                blf = u''

            func = u'fnc=sd+cp%s;sub=%s@$PROXY;nme=%s' % (blf, exten, label)

            if model in [u'SPA501G', u'SPA508G']:
                if key > 8:
                    key -= 8
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == u'SPA502G':
                if key > 2:
                    key -= 2
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == u'SPA504G':
                if key > 4:
                    key -= 4
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == u'SPA509G':
                if key > 12:
                    key -= 12
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif model == u'SPA525G' or model == u'SPA525G2':
                if key > 5:
                    key -= 5
                    fk_config_lines.append(self._format_function_keys_unit(key, func))
                    continue
            elif key > 12:
                continue

            fk_config_lines.append(u'<Extension_%d_>Disabled</Extension_%d_>' % (key, key))
            fk_config_lines.append(u'<Short_Name_%d_>%s</Short_Name_%d_>' % (key, label, key))
            fk_config_lines.append(u'<Extended_Function_%d_>%s</Extended_Function_%d_>' % (key, func, key))
        return u'\n'.join(fk_config_lines)
    
    def _get_xx_fkeys(self, config, model):
        return self._format_function_keys(config[u'funckeys'], model)
    
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
        return u'%s/%s/%s/%s:%s:%s' % (dst_change['month'], day, weekday, h, m, s)
    
    def _format_tzinfo(self, tzinfo):
        lines = []
        hours, minutes = tzinfo['utcoffset'].as_hms[:2]
        lines.append(u'<Time_Zone>GMT%+03d:%02d</Time_Zone>' % (hours, minutes))
        if tzinfo['dst'] is None:
            lines.append(u'<Daylight_Saving_Time_Enable>no</Daylight_Saving_Time_Enable>')
        else:
            lines.append(u'<Daylight_Saving_Time_Enable>yes</Daylight_Saving_Time_Enable>')
            h, m, s = tzinfo['dst']['save'].as_hms
            lines.append(u'<Daylight_Saving_Time_Rule>start=%s;end=%s;save=%d:%d:%s</Daylight_Saving_Time_Rule>' %
                         (self._format_dst_change(tzinfo['dst']['start']),
                          self._format_dst_change(tzinfo['dst']['end']),
                          h, m, s,
                          ))
        return u'\n'.join(lines)
    
    def _get_xx_timezone(self, raw_config):
        try:
            tzinfo = tzinform.get_timezone_info(raw_config.get(u'timezone'))
        except tzinform.TimezoneNotFoundError:
            return None
        else:
            return self._format_tzinfo(tzinfo)
    
    def _format_proxy(self, line):
        proxy_value = u'xivo_proxies:SRV=%s:5060:p=0' % line[u'proxy_ip']
        if u'backup_proxy_ip' in line:
            proxy_value += u'|%s:5060:p=1' % line[u'backup_proxy_ip']
        return proxy_value
    
    def _get_xx_proxies(self, raw_config):
        proxies = {}
        for line_no, line in raw_config[u'sip'][u'lines'].iteritems():
            proxies[line_no] = self._format_proxy(line)
        return proxies
    
    def _get_xx_language(self, raw_config):
        return self._XX_LANGUAGE.get(raw_config.get(u'locale'))
        
    def _dev_specific_filename(self, dev):
        # Return the device specific filename (not pathname) of device
        fmted_mac = format_mac(dev[u'mac'], separator='')
        return fmted_mac + '.xml'
    
    @classmethod
    def _check_config(cls, raw_config):
        if u'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')
        if u'sip' not in raw_config:
            raise RawConfigError('must have a sip parameter')
    
    def configure(self, device, raw_config):
        self._check_config(raw_config)
        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)
        
        raw_config[u'XX_fkeys'] = self._get_xx_fkeys(raw_config, device.get(u'model'))
        raw_config[u'XX_timezone'] = self._get_xx_timezone(raw_config)
        raw_config[u'XX_proxies'] = self._get_xx_proxies(raw_config)
        raw_config[u'XX_language'] = self._get_xx_language(raw_config)
        
        dst = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, dst, self._ENCODING)
    
    def deconfigure(self, device):
        path = os.path.join(self._tftpboot_dir, self._dev_specific_filename(device))
        try:
            os.remove(path)
        except OSError:
            # ignore -- probably an already removed file
            pass
    
    def synchronize(self, device, raw_config):
        try:
            ip = device[u'ip']
        except KeyError:
            return defer.fail(Exception('IP address needed for device synchronization'))
        else:
            def callback(status_code):
                if status_code == 200:
                    return None
                else:
                    e = Exception('SIP NOTIFY failed with status "%s"' % status_code)
                    return failure.Failure(e)
            for sip_line in raw_config[u'sip'][u'lines'].itervalues():
                username = sip_line[u'username']
                password = sip_line[u'password']
                break
            else:
                e = Exception('Need at least one configured line to resynchronize')
                return failure.Failure(e)
            uri = sip.URI('sip', ip, user=username, port=5060)
            d = sip.send_notify(uri, 'check-sync', (username, password))
            d.addCallback(callback)
            return d
