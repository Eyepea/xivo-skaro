# -*- coding: UTF-8 -*-

"""Common plugin code shared by the various xivo-cisco-sccp plugins.

Support most of the 7900 SCCP phones.

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

import contextlib
import cookielib
import logging
import os
import re
import urllib
import urllib2
from fetchfw.download import DefaultDownloader, InvalidCredentialsError,\
    DownloadError, new_handlers, new_downloaders
from fetchfw.storage import RemoteFileBuilder
from provd import tzinform
from provd.devices.config import RawConfigError
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    NO_SUPPORT, FULL_SUPPORT, COMPLETE_SUPPORT, PROBABLE_SUPPORT, \
    INCOMPLETE_SUPPORT
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.servers.tftp.service import TFTPFileService
from provd.services import PersistentConfigureServiceDecorator,\
    JsonConfigPersister
from provd.util import norm_mac, format_mac
from twisted.internet import defer

logger = logging.getLogger('plugin.xivo-cisco-sccp')


class WeakCiscoCredentialsError(DownloadError):
    pass


class CiscoDownloader(DefaultDownloader):
    _C14N_LOGIN_URL = 'http://www.cisco.com/cgi-bin/login'
    _POST_LOGIN_URL = 'https://fedps.cisco.com/idp/startSSO.ping?PartnerSpId=https://fedam.cisco.com&IdpAdapterId=fedsmidpCCO&TargetResource=http%3A//www.cisco.com/cgi-bin/login%3Freferer%3Dhttp%3A//www.cisco.com/'
    
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
            raise InvalidCredentialsError('no Cisco username/password have been set')
        if not self._is_authenticated:
            self._authenticate()
        assert self._is_authenticated
        f = self._opener.open(url)
        # Cisco website is not using HTTP 4xx status code to signal that we can't access an URL, so...
        if f.info().type == 'text/html':
            f.close()
            raise WeakCiscoCredentialsError('it seems like your Cisco username/password doesn\'t give you ' 
                                            'access to this URL (or this URL might be no longer valid)')
        return f
    
    def _authenticate(self):
        form_url = self._get_form_url()
        data = urllib.urlencode(self._form_params)
        logger.debug('Trying to authenticate on Cisco website')
        with contextlib.closing(self._opener.open(form_url, data)) as f:
            logger.debug('Checking for authentication failure - url "%s"', f.geturl())
            for line in f:
                if 'title' in line.lower():
                    if 'login' in line.lower():
                        break
                    else:
                        raise InvalidCredentialsError('authentification failed on Cisco website')
            else:
                logger.debug('No sign of authentication failure - assuming success')
        # Do GET request that sets more cookies and stuff. This is not done
        # automatically because:
        # - we don't support javascript
        # - we don't understand the HTML <meta http⁻equiv"refresh"> tag neither
        # This is extremely flimsy, but since we have no control on how cisco
        # handle the whole login process, this is as good as it can get.
        with contextlib.closing(self._opener.open(self._POST_LOGIN_URL)) as f:
            f.read()
        self._is_authenticated = True
        
    def _get_form_url(self):
        # This step is not strictly required but this way we have less chance to be
        # affected by an URL modification
        logger.debug('Getting Cisco form URL from C14N URL')
        with contextlib.closing(self._opener.open(self._C14N_LOGIN_URL)) as login:
            url = login.geturl()
            logger.debug('Form URL is "%s"', url)
            return url


class BaseCiscoPgAssociator(BasePgAssociator):
    _COMPAT_MODEL_REGEX = re.compile(ur'^79\d\dG$')
    
    def __init__(self, model_version):
        self._model_version = model_version
    
    def _do_associate(self, vendor, model, version):
        if vendor == u'Cisco':
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
            dev_info = {u'vendor':  u'Cisco'}
            m = self._VDI_REGEX.search(vdi)
            if m:
                model_num = m.group(1) or m.group(2)
                dev_info[u'model'] = u'79%sG' % model_num
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
                dev_info = {u'vendor': u'Cisco'}
                if m.lastindex == 1:
                    dev_info[u'mac'] = norm_mac(m.group(1))
                return dev_info


_ZONE_MAP = {
    'Etc/GMT+12': u'Dateline Standard Time',
    'Pacific/Samoa': u'Samoa Standard Time ',
    'US/Hawaii': u'Hawaiian Standard Time ',
    'US/Alaska': u'Alaskan Standard/Daylight Time',
    'US/Pacific': u'Pacific Standard/Daylight Time',
    'US/Mountain': u'Mountain Standard/Daylight Time',
    'Etc/GMT+7': u'US Mountain Standard Time',
    'US/Central': u'Central Standard/Daylight Time',
    'America/Mexico_City': u'Mexico Standard/Daylight Time',
#    '': u'Canada Central Standard Time',
#    '': u'SA Pacific Standard Time',
    'US/Eastern': u'Eastern Standard/Daylight Time',
    'Etc/GMT+5': u'US Eastern Standard Time',
    'Canada/Atlantic': u'Atlantic Standard/Daylight Time',
    'Etc/GMT+4': u'SA Western Standard Time',
    'Canada/Newfoundland': u'Newfoundland Standard/Daylight Time',
    'America/Sao_Paulo': u'South America Standard/Daylight Time',
    'Etc/GMT+3': u'SA Eastern Standard Time',
    'Etc/GMT+2': u'Mid-Atlantic Standard/Daylight Time',
    'Atlantic/Azores': u'Azores Standard/Daylight Time',
    'Europe/London': u'GMT Standard/Daylight Time',
    'Etc/GMT': u'Greenwich Standard Time',
#    'Europe/Belfast': u'W. Europe Standard/Daylight Time',
#    '': u'GTB Standard/Daylight Time',
    'Egypt': u'Egypt Standard/Daylight Time',
    'Europe/Athens': u'E. Europe Standard/Daylight Time',
#    'Europe/Rome': u'Romance Standard/Daylight Time',
    'Europe/Paris': u'Central Europe Standard/Daylight Time',
    'Africa/Johannesburg': u'South Africa Standard Time ',
    'Asia/Jerusalem': u'Jerusalem Standard/Daylight Time',
    'Asia/Riyadh': u'Saudi Arabia Standard Time',
    'Europe/Moscow': u'Russian Standard/Daylight Time', # Russia covers 8 time zones.
    'Iran': u'Iran Standard/Daylight Time',
#    '': u'Caucasus Standard/Daylight Time',
    'Etc/GMT-4': u'Arabian Standard Time',
    'Asia/Kabul': u'Afghanistan Standard Time ',
    'Etc/GMT-5': u'West Asia Standard Time',
#    '': u'Ekaterinburg Standard Time',
    'Asia/Calcutta': u'India Standard Time',
    'Etc/GMT-6': u'Central Asia Standard Time ',
    'Etc/GMT-7': u'SE Asia Standard Time',
#    '': u'China Standard/Daylight Time', # China doesn't observe DST since 1991
    'Asia/Taipei': u'Taipei Standard Time',
    'Asia/Tokyo': u'Tokyo Standard Time',
    'Australia/ACT': u'Cen. Australia Standard/Daylight Time',
    'Australia/Brisbane': u'AUS Central Standard Time',
#    '': u'E. Australia Standard Time',
#    '': u'AUS Eastern Standard/Daylight Time',
    'Etc/GMT-10': u'West Pacific Standard Time',
    'Australia/Tasmania': u'Tasmania Standard/Daylight Time',
    'Etc/GMT-11': u'Central Pacific Standard Time',
    'Etc/GMT-12': u'Fiji Standard Time',
#    '': u'New Zealand Standard/Daylight Time',
}


def _gen_tz_map():
    result = {}
    for tz_name, param_value in _ZONE_MAP.iteritems():
        tzinfo = tzinform.get_timezone_info(tz_name)
        inner_dict = result.setdefault(tzinfo['utcoffset'].as_minutes, {})
        if not tzinfo['dst']:
            inner_dict[None] = param_value
        else:
            inner_dict[tzinfo['dst']['as_string']] = param_value
    return result


class CiscoConfigureService(object):
    # implements(IConfigureService)
    
    def __init__(self, cisco_dler, username, password):
        # Creating an instance will also set the password to the downloader
        # if applicable
        self._cisco_dler = cisco_dler
        self._param_username = username
        self._param_password = password
        self._update_dler()
    
    def _update_dler(self):
        if self._param_username is not None and self._param_password is not None:
            self._cisco_dler.set_password(self._param_username, self._param_password)
    
    @staticmethod
    def _get_attr_name(name):
        # Return the key attribute name from the parameter name
        return '_param_' + name
    
    def get(self, name):
        try:
            return getattr(self, self._get_attr_name(name))
        except AttributeError, e:
            raise KeyError(e)
    
    def set(self, name, value):
        try:
            setattr(self, self._get_attr_name(name), value)
        except AttributeError, e:
            raise KeyError(e)
        else:
            self._update_dler()
    
    description = {
        u'username': u'The username used to download files from cisco.com website',
        u'password': u'The password used to download files from cisco.com website',
    }


class BaseCiscoSccpPlugin(StandardPlugin):
    # XXX actually, we didn't find which encoding Cisco SCCP are using
    _ENCODING = 'UTF-8'
    _TZ_MAP = _gen_tz_map()
    _TZ_VALUE_DEFAULT = u'Eastern Standard/Daylight Time'
    _XX_LANG = {
        u'de_DE': {
            u'name': u'german_germany',
            u'lang_code': u'de',
            u'network_locale': u'germany'
        },
        u'en_US': {
            u'name': u'english_united_states',
            u'lang_code': u'en',
            u'network_locale': u'united_states'
        },
        u'es_ES': {
            u'name': u'spanish_spain',
            u'lang_code': u'es',
            u'network_locale': u'spain'
        },
        u'fr_FR': {
            u'name': u'french_france',
            u'lang_code': u'fr',
            u'network_locale': u'france'
        },
        u'fr_CA': {
            u'name': u'french_france',
            u'lang_code': u'fr',
            u'network_locale': u'canada'
        }
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
        handlers = new_handlers(gen_cfg.get('proxies'))
        dlers = new_downloaders(handlers)
        cisco_dler = CiscoDownloader(handlers)
        dlers['x-cisco'] = cisco_dler
        rfile_builder = RemoteFileBuilder(dlers) 
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        
        cfg_service = CiscoConfigureService(cisco_dler, spec_cfg.get('username'),
                                            spec_cfg.get('password'))
        persister = JsonConfigPersister(os.path.join(self._plugin_dir, 'var',
                                                     'config.json'))
        cfg_service = PersistentConfigureServiceDecorator(cfg_service, persister)
        
        self.services = {'configure': cfg_service,
                         'install': fetchfw_helper}  
        self.tftp_service = TFTPFileService(self._tftpboot_dir)
    
    dhcp_dev_info_extractor = BaseCiscoDHCPDeviceInfoExtractor()
    
    tftp_dev_info_extractor = BaseCiscoTFTPDeviceInfoExtractor() 
    
    def _get_xx_language(self, config):
        xx_lang = None
        if u'locale' in config:
            locale = config[u'locale']
            if locale in self._XX_LANG:
                xx_lang = self._XX_LANG[locale]
        return xx_lang
    
    def _timezone_name_to_value(self, timezone):
        tzinfo = tzinform.get_timezone_info(timezone)
        utcoffset_m = tzinfo['utcoffset'].as_minutes
        if utcoffset_m not in self._TZ_MAP:
            # No UTC offset matching. Let's try finding one relatively close...
            for supp_offset in (30, -30, 60, -60):
                if utcoffset_m + supp_offset in self._TZ_MAP:
                    utcoffset_m += supp_offset
                    break
            else:
                return u'Central Europe Standard/Daylight Time'
            
        dst_map = self._TZ_MAP[utcoffset_m]
        if tzinfo['dst']:
            dst_key = tzinfo['dst']['as_string']
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
        if u'timezone' in config:
            timezone = config[u'timezone']
            tz_value = self._timezone_name_to_value(timezone)
        else:
            tz_value = self._TZ_VALUE_DEFAULT
        return tz_value
    
    def _dev_specific_filename(self, device):
        # Return the device specific filename (not pathname) of device
        fmted_mac = format_mac(device[u'mac'], separator='', uppercase=True)
        return 'SEP' + fmted_mac + '.cfg.xml'
    
    def _check_config(self, raw_config):
        if u'tftp_port' not in raw_config:
            raise RawConfigError('only support configuration via TFTP')
        if u'sccp' not in raw_config:
            raise RawConfigError('must have a sccp parameter')
    
    def _check_device(self, device):
        if u'mac' not in device:
            raise Exception('MAC address needed for device configuration')
    
    def configure(self, device, raw_config):
        self._check_config(raw_config)
        self._check_device(device)
        filename = self._dev_specific_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)
        
        # TODO check support for addons, and test what the addOnModules is
        #      really doing...
        raw_config[u'XX_addons'] = ''
        raw_config[u'XX_lang'] = self._get_xx_language(raw_config)
        raw_config[u'XX_timezone'] = self._get_xx_timezone(raw_config)
        
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
