# -*- coding: UTF-8 -*-

"""Common plugin code shared by the the various xivo-aastra plugins.

Support the 6730i, 6731i, 6739i, 6751i, 6753i, 6755i, 6757i.

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

import os.path
from provd import sip, tzinform
from provd.devices.config import RawConfigError
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.devices.pgasso import IMPROBABLE_SUPPORT, PROBABLE_SUPPORT,\
    INCOMPLETE_SUPPORT, COMPLETE_SUPPORT, FULL_SUPPORT, BasePgAssociator
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.python import failure


class BaseAastraHTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    _UA_MODELS_MAP = {
        'Aastra6730i': '6730i',     # not tested
        'Aastra6731i': '6731i',
        'Aastra6739i': '6739i',
        'Aastra51i': '6751i',       # not tested
        'Aastra53i': '6753i',       # not tested
        'Aastra55i': '6755i',
        'Aastra57i': '6757i',
    }
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_from_ua(ua, dev_info)
            if dev_info:
                dev_info['vendor'] = 'Aastra'
                return dev_info
    
    def _extract_from_ua(self, ua, dev_info):
        # HTTP User-Agent:
        #   "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.1008-SIP"
        #   "Aastra6731i MAC:00-08-5D-23-74-29 V:2.6.0.2010-SIP"
        #   "Aastra6739i MAC:00-08-5D-13-CA-05 V:3.0.1.2024-SIP"
        #   "Aastra55i MAC:00-08-5D-20-DA-5B V:2.6.0.1008-SIP"
        #   "Aastra57i MAC:00-08-5D-19-E4-01 V:2.6.0.1008-SIP"
        tokens = ua.split()
        if len(tokens) == 3:
            model_raw, mac_raw, version_raw = tokens
            model = self._parse_model(model_raw)
            if model:
                dev_info['model'] = model
            mac = self._parse_mac(mac_raw)
            if mac:
                dev_info['mac'] = mac
            version = self._parse_version(version_raw)
            if version:
                dev_info['version'] = version
    
    def _parse_model(self, model_raw):
        return self._UA_MODELS_MAP.get(model_raw)
    
    def _parse_mac(self, mac_raw):
        if mac_raw.startswith('MAC:'):
            # looks like a valid MAC token..
            try:
                return norm_mac(mac_raw[len('MAC:'):])
            except ValueError:
                pass
    
    def _parse_version(self, version_raw):
        if version_raw.startswith('V:') and version_raw.endswith('-SIP'):
            # looks like a valid version token...
            return version_raw[len('V:'):-len('-SIP')]


class BaseAastraPgAssociator(BasePgAssociator):
    def __init__(self, models, version, compat_models):
        BasePgAssociator.__init__(self)
        self._models = models
        self._version = version
        self._compat_models = compat_models
    
    def _do_associate(self, vendor, model, version):
        if vendor == 'Aastra':
            if model in self._models:
                if version == self._version:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            if model in self._compat_models:
                return INCOMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseAastraPlugin(StandardPlugin):
    _ENCODING = 'UTF-8'
    # XXX actually, we didn't find which encoding to use
    
    _XX_DICT_DEF = 'en'
    _XX_DICT = {
        'en': {
            'voicemail':  'Voicemail',
            'fwd_unconditional': 'Unconditional forward',
            'dnd': 'D.N.D',
            'local_directory': 'Directory',
            'callers': 'Callers',
            'services': 'Services',
            'pickup_call': 'Call pickup',
            'remote_directory': 'Directory',
        },
        'fr': {
            'voicemail':  'Messagerie',
            'fwd_unconditional': 'Renvoi inconditionnel',
            'dnd': 'N.P.D',
            'local_directory': 'Repertoire',
            'callers': 'Appels',
            'services': 'Services',
            'pickup_call': 'Interception',
            'remote_directory': 'Annuaire',
        },
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('http_proxy'))
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        self.services = self._fetchfw_helper.services() 
        
    http_dev_info_extractor = BaseAastraHTTPDeviceInfoExtractor()
    
    tftp_dev_info_extractor = None
    # This is not necessary since Aastra are capable of protocol
    # selection inside DHCP option 66 (TFTP server name).
    # That said, there is the rare case where one provisioning
    # server were replaced by this one, and the new one has the
    # same IP address than the old one and the phones were
    # configured to do TFTP and the admin guys are too lazy to
    # configure there DHCP server to change the value of option 66.
    # In this case, this might be useful.
    
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
        if model is None:
            return ''
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
    
    def _get_xx_fkeys(self, config, model):
        return self._format_function_keys(config['funckeys'], model)
    
    def _get_xx_timezone(self, config):
        # TODO handle the case where timezone is not present or is not a known
        #      timezone value
        return self._format_tz_inform(tzinform.get_timezone_info(config.get('timezone')))
    
    def _get_xx_dict(self, config):
        xx_dict = self._XX_DICT[self._XX_DICT_DEF]
        if 'locale' in config:
            locale = config['locale']
            lang = locale.split('_', 1)[0]
            if lang in self._XX_DICT:
                xx_dict = self._XX_DICT[lang]
        return xx_dict
    
    def _dev_specific_filename(self, dev):
        """Return the filename of the device specific configuration file of
        device dev.
        
        """
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        return fmted_mac + '.cfg'
    
    @classmethod
    def _check_config(cls, raw_config):
        if u'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')
        if u'sip' not in raw_config:
            raise RawConfigError('must have a sip parameter')
    
    def configure(self, dev, raw_config):
        self._check_config(raw_config)
        filename = self._dev_specific_filename(dev)
        tpl = self._tpl_helper.get_dev_template(filename, dev)
        
        raw_config['XX_fkeys'] = self._get_xx_fkeys(raw_config, dev.get('model'))
        raw_config['XX_timezone'] = self._get_xx_timezone(raw_config)
        raw_config['XX_dict'] = self._get_xx_dict(raw_config)
        
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
            return defer.fail(Exception('no IP address'))
        else:
            def on_notify_success(status_code):
                if status_code == 200:
                    return None
                else:
                    e = Exception('SIP NOTIFY failed with status "%s"' % status_code)
                    return failure.Failure(e)
            
            uri = sip.URI('sip', ip, port=5060)
            d = sip.send_notify(uri, 'check-sync')
            d.addCallback(on_notify_success)
            return d
