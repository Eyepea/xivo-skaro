# -*- coding: UTF-8 -*-

"""Common code shared by the the various xivo-aastra plugins.

Support the 6730i, 6731i, 6739i, 6751i, 6753i, 6755i, 6757i, 9143i and 9180i.

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

# XXX does the CT models identify themselves differently ? i.e. does the
#     57i CT identify itself as 57i or something like 57iCT ?
# TODO add function key support for 9143i and 9180i

import os.path
from provd import sip, tzinform
from provd.devices.config import RawConfigError
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.devices.pgasso import IMPROBABLE_SUPPORT, PROBABLE_SUPPORT,\
    INCOMPLETE_SUPPORT, COMPLETE_SUPPORT, FULL_SUPPORT, BasePgAssociator
from provd.servers.http import HTTPNoListingFileService
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.python import failure


class BaseAastraHTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    _UA_MODELS_MAP = {
        'Aastra6730i': u'6730i',     # not tested
        'Aastra6731i': u'6731i',
        'Aastra6739i': u'6739i',
        'Aastra51i': u'6751i',       # not tested
        'Aastra53i': u'6753i',       # not tested
        'Aastra55i': u'6755i',
        'Aastra57i': u'6757i',
        'Aastra9143i': u'9143i',     # not tested
        'Aastra9180i': u'9180i',     # not tested
    }
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_from_ua(ua, dev_info)
            if dev_info:
                dev_info[u'vendor'] = u'Aastra'
                return dev_info
        return None
    
    def _extract_from_ua(self, ua, dev_info):
        # HTTP User-Agent:
        #   "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.1008-SIP"
        #   "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.2010-SIP"
        #   "Aastra6739i MAC:00-08-5D-13-CA-05 V:3.0.1.2024-SIP"
        #   "Aastra55i MAC:00-08-5D-20-DA-5B V:2.6.0.1008-SIP"
        #   "Aastra57i MAC:00-08-5D-19-E4-01 V:2.6.0.1008-SIP"
        tokens = ua.split()
        if len(tokens) == 3:
            raw_model, raw_mac, raw_version = tokens
            model = self._parse_model(raw_model)
            if model:
                dev_info[u'model'] = model
            mac = self._parse_mac(raw_mac)
            if mac:
                dev_info[u'mac'] = mac
            version = self._parse_version(raw_version)
            if version:
                dev_info[u'version'] = version
        return None
    
    def _parse_model(self, raw_model):
        return self._UA_MODELS_MAP.get(raw_model)
    
    def _parse_mac(self, raw_mac):
        if raw_mac.startswith('MAC:'):
            # looks like a valid MAC token..
            try:
                return norm_mac(raw_mac[len('MAC:'):].decode('ascii'))
            except ValueError:
                pass
        return None
    
    def _parse_version(self, raw_version):
        if raw_version.startswith('V:') and raw_version.endswith('-SIP'):
            # looks like a valid version token...
            return raw_version[len('V:'):-len('-SIP')].decode('ascii')
        return None


class BaseAastraPgAssociator(BasePgAssociator):
    def __init__(self, models, version, compat_models):
        BasePgAssociator.__init__(self)
        self._models = models
        self._version = version
        self._compat_models = compat_models
    
    def _do_associate(self, vendor, model, version):
        if vendor == u'Aastra':
            if model in self._models:
                if version == self._version:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            if model in self._compat_models:
                return INCOMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseAastraPlugin(StandardPlugin):
    # Note that no TFTP support is included since Aastra phones are capable of
    # protocol selection via DHCP options.
    # XXX actually, we didn't find which encoding Aastra were using
    _ENCODING = 'UTF-8'
    _XX_DICT_DEF = u'en'
    _XX_DICT = {
        u'en': {
            u'voicemail':  u'Voicemail',
            u'fwd_unconditional': u'Unconditional forward',
            u'dnd': u'D.N.D',
            u'local_directory': u'Directory',
            u'callers': u'Callers',
            u'services': u'Services',
            u'pickup_call': u'Call pickup',
            u'remote_directory': u'Directory',
        },
        u'fr': {
            u'voicemail':  u'Messagerie',
            u'fwd_unconditional': u'Renvoi inconditionnel',
            u'dnd': u'N.P.D',
            u'local_directory': u'Repertoire',
            u'callers': u'Appels',
            u'services': u'Services',
            u'pickup_call': u'Interception',
            u'remote_directory': u'Annuaire',
        },
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        
        self.services = fetchfw_helper.services()
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
    
    http_dev_info_extractor = BaseAastraHTTPDeviceInfoExtractor()
    
    def _format_expmod(self, keynum):
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
            return u'expmod%d key%d' % ((keynum - 1) // 60 + 1, (keynum - 1) % 60 + 1)
        return None
    
    def _get_keytype_from_model_and_keynum(self, model, keynum):
        if model in [u'6730i', u'6731i']:
            if keynum <= 8:
                return u'prgkey%d' % keynum
        elif model == '6739i':
            if keynum <= 55:
                return u'softkey%d' % keynum
            else:
                return self._format_expmod(keynum - 55)
        elif model == u'6753i':
            if keynum <= 6:
                return u'prgkey%d' % keynum
            else:
                return self._format_expmod(keynum - 6)
        elif model == u'6755i':
            if keynum <= 6:
                return u'prgkey%d' % keynum
            else:
                keynum -= 6
                if keynum <= 20:
                    return u'softkey%d' % keynum
                else:
                    return self._format_expmod(keynum - 20)
        elif model == u'6757i':
            # The 57i has 6 'top keys' and 6 'bottom keys'. 10 functions are programmable for
            # the top keys and 20 are for the bottom keys.
            if keynum <= 10:
                return u'topsoftkey%d' % keynum
            else:
                keynum -= 10
                if keynum <= 20:
                    return u'softkey%d' % keynum
                else:
                    return self._format_expmod(keynum - 20)
        return None
    
    def _format_function_keys(self, funckeys, model):
        if model is None:
            return u''
        sorted_keys = funckeys.keys()
        sorted_keys.sort()
        fk_config_lines = []
        for key in sorted_keys:
            keytype = self._get_keytype_from_model_and_keynum(model, int(key))
            if keytype is not None:
                value = funckeys[key]
                exten = value[u'exten']
                if value.get(u'supervision'):
                    xtype = u'blf'
                else:
                    xtype = u'speeddial'
                if u'label' in value and value[u'label'] is not None:
                    label = value[u'label']
                else:
                    label = exten
                line = value.get(u'line', 1)
                fk_config_lines.append(u'%s type: %s' % (keytype, xtype))
                fk_config_lines.append(u'%s label: %s' % (keytype, label))
                fk_config_lines.append(u'%s value: %s' % (keytype, exten))
                fk_config_lines.append(u'%s line: %s' % (keytype, line))
        return u'\n'.join(fk_config_lines)
    
    def _format_dst_change(self, suffix, dst_change):
        lines = []
        lines.append(u'dst %s month: %d' % (suffix, dst_change['month']))
        lines.append(u'dst %s hour: %d' % (suffix, min(dst_change['time'].as_hours, 23)))
        if dst_change['day'].startswith('D'):
            lines.append(u'dst %s day: %s' % (suffix, dst_change['day'][1:]))
        else:
            week, weekday = dst_change['day'][1:].split('.')
            if week == '5':
                lines.append(u'dst %s week: -1' % suffix)
            else:
                lines.append(u'dst %s week: %s' % (suffix, week))
            lines.append(u'dst %s day: %s' % (suffix, weekday))
        return lines
    
    def _format_tzinfo(self, tzinfo):
        lines = []
        lines.append(u'time zone name: Custom')
        lines.append(u'time zone minutes: %d' % -(tzinfo['utcoffset'].as_minutes))
        if tzinfo['dst'] is None:
            lines.append(u'dst config: 0')
        else:
            lines.append(u'dst config: 3')
            lines.append(u'dst minutes: %d' % (min(tzinfo['dst']['save'].as_minutes, 60)))
            if tzinfo['dst']['start']['day'].startswith('D'):
                lines.append(u'dst [start|end] relative date: 0')
            else:
                lines.append(u'dst [start|end] relative date: 1')
            lines.extend(self._format_dst_change('start', tzinfo['dst']['start']))
            lines.extend(self._format_dst_change('end', tzinfo['dst']['end']))
        return u'\n'.join(lines)
    
    def _get_xx_fkeys(self, raw_config, model):
        return self._format_function_keys(raw_config[u'funckeys'], model)
    
    def _get_xx_timezone(self, raw_config):
        try:
            tzinfo = tzinform.get_timezone_info(raw_config.get(u'timezone'))
        except tzinform.TimezoneNotFoundError:
            return None
        else:
            return self._format_tzinfo(tzinfo)
    
    def _get_xx_dict(self, raw_config):
        xx_dict = self._XX_DICT[self._XX_DICT_DEF]
        if u'locale' in raw_config:
            locale = raw_config[u'locale']
            lang = locale.split('_', 1)[0]
            if lang in self._XX_DICT:
                xx_dict = self._XX_DICT[lang]
        return xx_dict
    
    def _dev_specific_filename(self, device):
        # Return the device specific filename (not pathname) of device
        fmted_mac = format_mac(device[u'mac'], separator='', uppercase=True)
        return fmted_mac + '.cfg'
    
    def _check_config(self, raw_config):
        if u'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')
        if u'sip' not in raw_config:
            raise RawConfigError('must have a sip parameter')
    
    def _check_device(self, device):
        if u'mac' not in device:
            raise Exception('MAC address needed for device configuration')
    
    def configure(self, device, raw_config):
        self._check_config(raw_config)
        self._check_device(device)
        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)
        
        raw_config[u'XX_fkeys'] = self._get_xx_fkeys(raw_config, device.get(u'model'))
        raw_config[u'XX_timezone'] = self._get_xx_timezone(raw_config)
        raw_config[u'XX_dict'] = self._get_xx_dict(raw_config)
        
        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)
    
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
            uri = sip.URI('sip', ip, port=5060)
            d = sip.send_notify(uri, 'check-sync')
            d.addCallback(callback)
            return d
