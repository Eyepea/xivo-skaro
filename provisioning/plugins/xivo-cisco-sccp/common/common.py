# -*- coding: UTF-8 -*-

"""Common plugin code shared by the various xivo-cisco-sccp plugins.

Support most of the SCCP phones, in variable quality.

This plugin defines 2 configuration key:

username -- the username to use to download files on cisco.com website
password -- the password to use to download files on cisco.com website

"""

from __future__ import with_statement

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

import contextlib
import cookielib
import os
import re
import urllib
import urllib2
from fetchfw.download import DefaultDownloader, InvalidCredentialsError,\
    DownloadError, new_handlers, new_downloaders
from fetchfw.storage import RemoteFileBuilder
from provd.devices.config import RawConfigError
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    NO_SUPPORT, FULL_SUPPORT, COMPLETE_SUPPORT, PROBABLE_SUPPORT, \
    INCOMPLETE_SUPPORT
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from xivo import tzinform


class WeakCiscoCredentialsError(DownloadError):
    pass


class CiscoDownloader(DefaultDownloader):
    # XXX no provision for logging right now, that's why there's 'logger' line
    #     commented
    _C14N_LOGIN_URL = 'http://www.cisco.com/cgi-bin/login'
    
    def __init__(self, handlers):
        DefaultDownloader.__init__(self, handlers)
        self._cookiejar = cookielib.CookieJar()
        self._opener.add_handler(urllib2.HTTPCookieProcessor(self._cookiejar))
        self._form_params = None
        self._is_authenticated = False
    
    def set_password(self, user, passwd):
        self._is_authenticated = False
        self._cookiejar.clear()
        self._form_params = {'USER': user, 'PASSWORD': passwd}
    
    def _do_download(self, url):
        if not self._form_params:
            raise InvalidCredentialsError("no Cisco username/password have been set")
        if not self._is_authenticated:
            self._authenticate()
        assert self._is_authenticated
        f = self._opener.open(url)
        # Cisco website is not using HTTP 4xx status code to signal that we can't access an URL, so...
        if f.info().type == 'text/html':
            f.close()
            raise WeakCiscoCredentialsError("it seems like your Cisco username/password doesn't give you " 
                                            "access to this URL (or this URL might be no longer valid)")
        return f
    
    def _authenticate(self):
        form_url = self._get_form_url()
        data = urllib.urlencode(self._form_params)
        #logger.debug('Trying to authenticate on Cisco website')
        with contextlib.closing(self._opener.open(form_url, data)) as f:
            #logger.debug("Checking for authentication failure - url '%s'", f.geturl())
            for line in f:
                if 'title' in line.lower():
                    if 'login' in line.lower():
                        break
                    else:
                        raise InvalidCredentialsError("authentification failed on Cisco website")
            else:
                #logger.debug("No sign of authentication failure - assuming success")
                pass
        self._is_authenticated = True
        
    def _get_form_url(self):
        # This step is not strictly required but this way we have less chance to be
        # affected by an URL modification
        #logger.debug('Getting Cisco form URL from C14N URL')
        with contextlib.closing(self._opener.open(self._C14N_LOGIN_URL)) as login:
            url = login.geturl()
            #logger.debug("Form URL is '%s'", url)
            return url


class BaseCiscoPgAssociator(BasePgAssociator):
    _COMPAT_MODEL_REGEX = re.compile(r'^79\d\dG$')
    
    def __init__(self, model_version):
        self._model_version = model_version
    
    def _do_associate(self, vendor, model, version):
        if vendor == 'Cisco':
            if version is None:
                # Could be either in SIP or SCCP...
                return PROBABLE_SUPPORT
            if model is None:
                # There's so many Cisco models it's hard to say something
                # precise when we have no model information
                return PROBABLE_SUPPORT
            assert version is not None
            assert model is not None
            if version.endswith('/SIP'):
                return NO_SUPPORT
            if model in self._model_version:
                if version == self._model_version[model]:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            if self._COMPAT_MODEL_REGEX.match(model):
                return INCOMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseCiscoDHCPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'dhcp'
        return defer.succeed(self._do_extract(request))
    
    _VDI_REGEX = re.compile('\\s(?:79(\\d\\d)|CP-79(\\d\\d)G(?:-GE)?\x00)$')
    
    def _do_extract(self, request):
        options = request[u'options']
        if 60 in options:
            return self._extract_from_vdi(options[60])
    
    def _extract_from_vdi(self, vdi):
        # Vendor class identifier:
        #   "Cisco Systems, Inc. IP Phone 7912" (Cisco 7912 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7940G\x00" (Cisco 7940 8.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-7941G\x00" (Cisco 7941 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7960G\x00" (Cisco 7960 8.1.2)
        if vdi.startswith('Cisco Systems, Inc. IP Phone'):
            dev_info = {'vendor':  'Cisco'}
            m = self._VDI_REGEX.search(vdi)
            if m:
                model_num = m.group(1) or m.group(2)
                dev_info['model'] = '79' + model_num + 'G'
            return dev_info


class BaseCiscoTFTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'tftp'
        return defer.succeed(self._do_extract(request))
    
    _FILENAME_REGEX = [
        # We know this pattern is not unique to the 7900
        re.compile(r'^SEP([\dA-F]{12})\.cnf\.xml$'),
        re.compile(r'^CTLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLFile\.tlv$'),
        re.compile(r'^g3-tones\.xml$'),
    ]
    
    def _do_extract(self, request):
        packet = request['packet']
        filename = packet['filename']
        for regex in self._FILENAME_REGEX:
            m = regex.match(filename)
            if m:
                dev_info = {'vendor': 'Cisco'}
                if m.lastindex == 1:
                    dev_info['mac'] = norm_mac(m.group(1))
                return dev_info


_ZONE_MAP = {
    'Etc/GMT+12': 'Dateline Standard Time',
    'Pacific/Samoa': 'Samoa Standard Time ',
    'US/Hawaii': 'Hawaiian Standard Time ',
    'US/Alaska': 'Alaskan Standard/Daylight Time',
    'US/Pacific': 'Pacific Standard/Daylight Time',
    'US/Mountain': 'Mountain Standard/Daylight Time',
    'Etc/GMT+7': 'US Mountain Standard Time',
    'US/Central': 'Central Standard/Daylight Time',
    'America/Mexico_City': 'Mexico Standard/Daylight Time',
#    '': 'Canada Central Standard Time',
#    '': 'SA Pacific Standard Time',
    'US/Eastern': 'Eastern Standard/Daylight Time',
    'Etc/GMT+5': 'US Eastern Standard Time',
    'Canada/Atlantic': 'Atlantic Standard/Daylight Time',
    'Etc/GMT+4': 'SA Western Standard Time',
    'Canada/Newfoundland': 'Newfoundland Standard/Daylight Time',
    'America/Sao_Paulo': 'South America Standard/Daylight Time',
    'Etc/GMT+3': 'SA Eastern Standard Time',
    'Etc/GMT+2': 'Mid-Atlantic Standard/Daylight Time',
    'Atlantic/Azores': 'Azores Standard/Daylight Time',
    'Europe/London': 'GMT Standard/Daylight Time',
    'Etc/GMT': 'Greenwich Standard Time',
#    'Europe/Belfast': 'W. Europe Standard/Daylight Time',
#    '': 'GTB Standard/Daylight Time',
    'Egypt': 'Egypt Standard/Daylight Time',
    'Europe/Athens': 'E. Europe Standard/Daylight Time',
#    'Europe/Rome': 'Romance Standard/Daylight Time',
    'Europe/Paris': 'Central Europe Standard/Daylight Time',
    'Africa/Johannesburg': 'South Africa Standard Time ',
    'Asia/Jerusalem': 'Jerusalem Standard/Daylight Time',
    'Asia/Riyadh': 'Saudi Arabia Standard Time',
    'Europe/Moscow': 'Russian Standard/Daylight Time', # Russia covers 8 time zones.
    'Iran': 'Iran Standard/Daylight Time',
#    '': 'Caucasus Standard/Daylight Time',
    'Etc/GMT-4': 'Arabian Standard Time',
    'Asia/Kabul': 'Afghanistan Standard Time ',
    'Etc/GMT-5': 'West Asia Standard Time',
#    '': 'Ekaterinburg Standard Time',
    'Asia/Calcutta': 'India Standard Time',
    'Etc/GMT-6': 'Central Asia Standard Time ',
    'Etc/GMT-7': 'SE Asia Standard Time',
#    '': 'China Standard/Daylight Time', # China doesn't observe DST since 1991
    'Asia/Taipei': 'Taipei Standard Time',
    'Asia/Tokyo': 'Tokyo Standard Time',
    'Australia/ACT': 'Cen. Australia Standard/Daylight Time',
    'Australia/Brisbane': 'AUS Central Standard Time',
#    '': 'E. Australia Standard Time',
#    '': 'AUS Eastern Standard/Daylight Time',
    'Etc/GMT-10': 'West Pacific Standard Time',
    'Australia/Tasmania': 'Tasmania Standard/Daylight Time',
    'Etc/GMT-11': 'Central Pacific Standard Time',
    'Etc/GMT-12': 'Fiji Standard Time',
#    '': 'New Zealand Standard/Daylight Time',
}


def _gen_tz_map():
    result = {}
    for tz_name, param_value in _ZONE_MAP.iteritems():
        inform = tzinform.get_timezone_info(tz_name)
        inner_dict = result.setdefault(inform['utcoffset'].as_minutes, {})
        if not inform['dst']:
            inner_dict[None] = param_value
        else:
            inner_dict[inform['dst']['as_string']] = param_value
    return result


class BaseCiscoSccpPlugin(StandardPlugin):
    _ENCODING = 'UTF-8'
    # XXX actually, we didn't find which encoding to use
    
    _XX_LANG = {
        'de_DE': {
            'name': 'german_germany',
            'lang_code': 'de',
            'network_locale': 'germany'
        },
        'en_US': {
            'name': 'english_united_states',
            'lang_code': 'en',
            'network_locale': 'united_states'
        },
        'es_ES': {
            'name': 'spanish_spain',
            'lang_code': 'es',
            'network_locale': 'spain'
        },
        'fr_FR': {
            'name': 'french_france',
            'lang_code': 'fr',
            'network_locale': 'france'
        },
        'fr_CA': {
            'name': 'french_france',
            'lang_code': 'fr',
            'network_locale': 'canada'
        }
    }
    
    _TZ_MAP = _gen_tz_map()
    _TZ_VALUE_DEFAULT = 'Eastern Standard/Daylight Time'
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        handlers = new_handlers(gen_cfg.get('http_proxy'))
        dlers = new_downloaders(handlers)
        self._cisco_dler = CiscoDownloader(handlers)
        if 'username' in spec_cfg and 'password' in spec_cfg:
            self._cisco_dler.set_password(spec_cfg['username'], spec_cfg['password'])
        dlers['x-cisco'] = self._cisco_dler
        rfile_builder = RemoteFileBuilder(dlers) 
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        # TODO add configure service...
        self.services = self._fetchfw_helper.services() 
    
    dhcp_dev_info_extractor = BaseCiscoDHCPDeviceInfoExtractor()
    tftp_dev_info_extractor = BaseCiscoTFTPDeviceInfoExtractor() 
    
    def _get_xx_language(self, config):
        xx_lang = None
        if 'locale' in config:
            locale = config['locale']
            if locale in self._XX_LANG:
                xx_lang = self._XX_LANG[locale]
        return xx_lang
    
    def _timezone_name_to_value(self, timezone):
        inform = tzinform.get_timezone_info(timezone)
        utcoffset_m = inform['utcoffset'].as_minutes
        if utcoffset_m not in self._TZ_MAP:
            # No UTC offset matching. Let's try finding one relatively close...
            for supp_offset in (30, -30, 60, -60):
                if utcoffset_m + supp_offset in self._TZ_MAP:
                    utcoffset_m += supp_offset
                    break
            else:
                return "Central Europe Standard/Daylight Time"
            
        dst_map = self._TZ_MAP[utcoffset_m]
        if inform['dst']:
            dst_key = inform['dst']['as_string']
        else:
            dst_key = None
        if dst_key not in dst_map:
            # No DST rules matching. Fallback on all-standard time or random
            # DST rule in last resort...
            if None in dst_map:
                dst_key = None
            else:
                dst_key = dst_map.keys[0]
        return dst_map[dst_key]
    
    def _get_xx_timezone(self, config):
        if 'timezone' in config:
            timezone = config['timezone']
            tz_value = self._timezone_name_to_value(timezone)
        else:
            tz_value = self._TZ_VALUE_DEFAULT
        return tz_value
    
    def _dev_specific_filename(self, dev):
        """Return the filename of the device specific configuration file of
        device dev.
        
        """
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        return 'SEP' + fmted_mac + '.cfg.xml'
    
    @classmethod
    def _check_config(cls, raw_config):
        if u'tftp_port' not in raw_config:
            raise RawConfigError('only support configuration via TFTP')
        if raw_config[u'protocol'] != u'SCCP':
            raise RawConfigError('protocol must be SCCP')
    
    def configure(self, dev, raw_config):
        self._check_config(raw_config)
        filename = self._dev_specific_filename(dev)
        tpl = self._tpl_helper.get_dev_template(filename, dev)
        
        # TODO check support for addons, and test what the addOnModules is
        #      really doing...
        raw_config['XX_addons'] = ''
        raw_config['XX_lang'] = self._get_xx_language(raw_config)
        raw_config['XX_timezone'] = self._get_xx_timezone(raw_config)
        
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
        # The only known way to synchronize SCCP device is to do an
        # 'sccp reload' or 'sccp restart' or similar from Asterisk
        return defer.fail(Exception('Resynchronization not supported for SCCP devices'))
