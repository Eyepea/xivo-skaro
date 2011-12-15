# -*- coding: UTF-8 -*-

"""Common plugin code shared by the various xivo-cisco-sccp and
xivo-cisco-sip plugins.

"""

__license__ = """
    Copyright (C) 2010-2011  Avencall

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
import re
import urllib
import urllib2
from fetchfw.download import DefaultDownloader, InvalidCredentialsError,\
    DownloadError
from provd import tzinform
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    NO_SUPPORT, FULL_SUPPORT, COMPLETE_SUPPORT, PROBABLE_SUPPORT
from provd.util import norm_mac
from twisted.internet import defer

logger = logging.getLogger('plugin.xivo-cisco')


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
    
    def clear_password(self):
        self._form_params = None
    
    def set_password(self, user, passwd):
        self._is_authenticated = False
        self._cookiejar.clear()
        self._form_params = {'USER': user, 'PASSWORD': passwd}
    
    def _do_download(self, url, timeout):
        if not self._form_params:
            raise InvalidCredentialsError('no Cisco username/password have been set')
        if not self._is_authenticated:
            self._authenticate(timeout)
        assert self._is_authenticated
        f = self._opener.open(url, timeout=timeout)
        # Cisco website is not using HTTP 4xx status code to signal that we can't access an URL, so...
        if f.info().type == 'text/html':
            f.close()
            raise WeakCiscoCredentialsError('it seems like your Cisco username/password doesn\'t give you ' 
                                            'access to this URL (or this URL might be no longer valid)')
        return f
    
    def _authenticate(self, timeout):
        form_url = self._get_form_url(timeout)
        data = urllib.urlencode(self._form_params)
        logger.debug('Trying to authenticate on Cisco website')
        with contextlib.closing(self._opener.open(form_url, data, timeout=timeout)) as f:
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
        with contextlib.closing(self._opener.open(self._POST_LOGIN_URL, timeout=timeout)) as f:
            f.read()
        self._is_authenticated = True
        
    def _get_form_url(self, timeout):
        # This step is not strictly required but this way we have less chance to be
        # affected by an URL modification
        logger.debug('Getting Cisco form URL from C14N URL')
        with contextlib.closing(self._opener.open(self._C14N_LOGIN_URL, timeout=timeout)) as login:
            url = login.geturl()
            logger.debug('Form URL is "%s"', url)
            return url


class BaseCiscoPgAssociator(BasePgAssociator):
    def __init__(self, model_version):
        self._model_version = model_version
    
    def _do_associate(self, vendor, model, version):
        if vendor == u'Cisco':
            if model is None:
                # There's so many Cisco models it's hard to say something
                # precise when we have no model information
                return PROBABLE_SUPPORT
            assert model is not None
            if model.startswith(u'SPA'):
                return NO_SUPPORT
            if version is None:
                # Could be either in SIP or SCCP...
                return PROBABLE_SUPPORT
            assert version is not None
            if model in self._model_version:
                if version == self._model_version[model]:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BaseCiscoDHCPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        return defer.succeed(self._do_extract(request))
    
    _VDI_REGEX = re.compile(r'IP Phone (?:79(\d\d)|CP-79(\d\d)G|CP-(\d\d\d\d))')
    
    def _do_extract(self, request):
        options = request[u'options']
        if 60 in options:
            return self._extract_from_vdi(options[60])
    
    def _extract_from_vdi(self, vdi):
        # Vendor class identifier:
        #   "Cisco Systems, Inc." (Cisco 6901 9.1.2/9.2.1)
        #   "Cisco Systems, Inc. IP Phone 7912" (Cisco 7912 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7940G\x00" (Cisco 7940 8.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-7941G\x00" (Cisco 7941 9.0.3)
        #   "Cisco Systems, Inc. IP Phone CP-7960G\x00" (Cisco 7960 8.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-8961\x00" (Cisco 8961 9.1.2)
        #   "Cisco Systems, Inc. IP Phone CP-9951\x00" (Cisco 9951 9.1.2)
        if vdi.startswith('Cisco Systems, Inc.'):
            dev_info = {u'vendor':  u'Cisco'}
            m = self._VDI_REGEX.search(vdi)
            if m:
                _7900_modelnum = m.group(1) or m.group(2)
                if _7900_modelnum:
                    dev_info[u'model'] = u'79%sG' % _7900_modelnum
                else:
                    model_num = m.group(3)
                    dev_info[u'model'] = model_num.decode('ascii')
            return dev_info


class BaseCiscoTFTPDeviceInfoExtractor(object):
    _FILENAME_REGEXES = [
        re.compile(r'^SEP([\dA-F]{12})\.cnf\.xml$'),
        re.compile(r'^CTLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLSEP([\dA-F]{12})\.tlv$'),
        re.compile(r'^ITLFile\.tlv$'),
        re.compile(r'^g3-tones\.xml$'),
    ]
    
    def extract(self, request, request_type):
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        packet = request['packet']
        filename = packet['filename']
        for regex in self._FILENAME_REGEXES:
            m = regex.match(filename)
            if m:
                dev_info = {u'vendor': u'Cisco'}
                if m.lastindex == 1:
                    try:
                        dev_info[u'mac'] = norm_mac(m.group(1).decode('ascii'))
                    except ValueError, e:
                        logger.warning('Could not normalize MAC address: %s', e)
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
        self._p_username = username
        self._p_password = password
        self._update_dler()
    
    def _update_dler(self):
        if self._p_username and self._p_password:
            self._cisco_dler.set_password(self._p_username, self._p_password)
        else:
            self._cisco_dler.clear_password()
    
    def get(self, name):
        try:
            return getattr(self, '_p_' + name)
        except AttributeError, e:
            raise KeyError(e)
    
    def set(self, name, value):
        attrname = '_p_' + name
        if hasattr(self, attrname):
            setattr(self, attrname, value)
            self._update_dler()
        else:
            raise KeyError(name)
    
    description = [
        (u'username', u'The username used to download files from cisco.com website'),
        (u'password', u'The password used to download files from cisco.com website'),
    ]
    
    description_fr = [
        (u'username', u"Le nom d'utilisateur pour télécharger les fichiers sur le site cisco.com"),
        (u'password', u'Le mot de passe pour télécharger les fichiers sur le site cisco.com'),
    ]
