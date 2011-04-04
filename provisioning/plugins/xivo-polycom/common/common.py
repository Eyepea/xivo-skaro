# -*- coding: UTF-8 -*-

"""Common code shared by the the various xivo-polycom plugins.

Support the IP301, IP320, IP321, IP330, IP331, IP335, IP430, IP450, IP501,
IP550, IP560, IP600, IP601, IP650, IP670, IP4000, IP5000, IP6000, IP7000 and
VVX1500.

"""

__version__ = "$Revision: 10288 $ $Date: 2011-03-02 08:58:26 -0500 (Wed, 02 Mar 2011) $"
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

# TODO add DHCP device info extractor ? (see admin guide p.374)

import logging
import re
import os.path
from provd import sip
from provd import tzinform
from provd.devices.config import RawConfigError
from provd.devices.pgasso import IMPROBABLE_SUPPORT, PROBABLE_SUPPORT,\
    COMPLETE_SUPPORT, FULL_SUPPORT, BasePgAssociator
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.servers.http import HTTPNoListingFileService
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.python import failure

logger = logging.getLogger('plugin.xivo-polycom')


class BasePolycomHTTPDeviceInfoExtractor(object):
    _UA_REGEX = re.compile(r'^FileTransport Polycom\w+-(\w*?)-UA/([\d.]+)$')
    _PATH_REGEX = re.compile(r'/(?!000000000000)([\da-f]{12})(?:\.cfg|-boot\.log|-phone\.cfg|-license\.cfg|-directory\.xml|-app\.log)$')
    _IS_SIPAPP_REGEX = re.compile(r'/(?:(?:common\.cfg|phone1\.cfg|sip\.cfg)|(?:[\da-f]{12}-(?:phone\.cfg|license\.cfg|directory\.xml|app\.log)))$')
    
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_info_from_ua(ua, dev_info)
            if dev_info:
                path = request.path
                if u'version' in dev_info and not self._is_sip_application_request(path):
                    del dev_info[u'version']
                self._extract_mac_from_path(path, dev_info)
                return dev_info
        return None
    
    def _extract_info_from_ua(self, ua, dev_info):
        # Note: depending on the boot step, the version number will either
        # be the BootROM version (first few requests) or the SIP application
        # version (later on in the boot process).
        # HTTP User-Agent:
        #   "FileTransport PolycomSoundPointIP-SPIP_335-UA/3.2.1.0078" (SPIP335 3.2.1.0078/4.2.1.0275)
        #   "FileTransport PolycomSoundPointIP-SPIP_335-UA/4.2.1.0275" (SPIP335 3.2.1.0078/4.2.1.0275)
        #   "FileTransport PolycomSoundPointIP-SPIP_335-UA/3.2.3.1734" (SPIP335 3.2.3.1734/4.2.2.0710)
        #   "FileTransport PolycomSoundPointIP-SPIP_335-UA/4.2.2.0710" (SPIP335 3.2.3.1734/4.2.2.0710)
        #   "FileTransport PolycomSoundPointIP-SPIP_450-UA/3.2.3.1734" (SPIP450 3.2.3.1734/4.2.2.0710)
        #   "FileTransport PolycomSoundPointIP-SPIP_550-UA/3.2.3.1734" (SPIP335 3.2.3.1734/4.2.2.0710)
        m = self._UA_REGEX.match(ua)
        if m:
            dev_info[u'vendor'] = u'Polycom'
            raw_model, raw_version = m.groups()
            dev_info[u'model'] = raw_model.replace('_', '').decode('ascii')
            dev_info[u'version'] = raw_version.decode('ascii')
    
    def _extract_mac_from_path(self, path, dev_info):
        # Extract the MAC address from the requested path if possible
        m = self._PATH_REGEX.search(path)
        if m:
            raw_mac = m.group(1)
            dev_info[u'mac'] = norm_mac(raw_mac.decode('ascii'))
    
    def _is_sip_application_request(self, path):
        # Return true if path has been requested by the SIP application (and
        # not the BootROM). This use the fact that some files are only
        # request by the SIP application.
        return bool(self._IS_SIPAPP_REGEX.search(path))


class BasePolycomPgAssociator(BasePgAssociator):
    def __init__(self, models, version):
        BasePgAssociator.__init__(self)
        self._models = models
        self._version = version
    
    def _do_associate(self, vendor, model, version):
        if vendor == u'Polycom':
            if model in self._models:
                if version == self._version:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class BasePolycomPlugin(StandardPlugin):
    # Note that no TFTP support is included since Polycom phones are capable of
    # protocol selection via DHCP options.
    _ENCODING = 'UTF-8'
    _NB_FKEY_MAP = {
        u'SPIP450': 2,
        u'SPIP550': 3,
        u'SPIP560': 3,
        u'SPIP650': 47,
        u'SPIP670': 47,
    }
    _XX_LANGUAGE_MAP = {
        u'de_DE': u'German_Germany',
        u'en_US': u'English_United_States',
        u'es_ES': u'Spanish_Spain',
        u'fr_FR': u'French_France',
        u'fr_CA': u'French_France',
    }
    _XX_SYSLOG_LEVEL = {
        u'critical': 5,
        u'error': 4,
        u'warning': 3,
        u'info': 2,
        u'debug': 1
    }
    _XX_SYSLOG_LEVEL_DEF = 1
    _XX_SIP_TRANSPORT = {
        u'udp': u'UDPOnly',
        u'tcp': u'TCPOnly',
        u'tls': u'TLS'
    }
    _XX_SIP_TRANSPORT_DEF = u'UDPOnly'
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('proxies'))
        fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        
        self.services = fetchfw_helper.services() 
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
    
    http_dev_info_extractor = BasePolycomHTTPDeviceInfoExtractor()
    
    def _format_dst_change(self, suffix, dst_change):
        lines = []
        lines.append(u'tcpIpApp.sntp.daylightSavings.%s.month="%d"' % (suffix, dst_change['month']))
        lines.append(u'tcpIpApp.sntp.daylightSavings.%s.time="%d"' % (suffix, dst_change['time'].as_hours))
        if dst_change['day'].startswith('D'):
            lines.append(u'tcpIpApp.sntp.daylightSavings.%s.date="%s"' % (suffix, dst_change['day'][1:]))
        else:
            week, weekday = dst_change['day'][1:].split('.')
            lines.append(u'tcpIpApp.sntp.daylightSavings.%s.dayOfWeek="%s"' % (suffix, weekday))
            if week == '5':
                lines.append(u'tcpIpApp.sntp.daylightSavings.%s.dayOfWeek.lastInMonth="1"' % suffix)
            else:
                lines.append(u'tcpIpApp.sntp.daylightSavings.%s.dayOfWeek.lastInMonth="0"' % suffix)
                lines.append(u'tcpIpApp.sntp.daylightSavings.%s.date="%d"' % (suffix, (int(week) - 1) * 7 + 1))
        return lines
    
    def _format_tzinfo(self, tzinfo):
        lines = []
        lines.append(u'tcpIpApp.sntp.gmtOffset="%d"' % tzinfo['utcoffset'].as_seconds)
        if tzinfo['dst'] is None:
            lines.append(u'tcpIpApp.sntp.daylightSavings.enable="0"')
        else:
            lines.append(u'tcpIpApp.sntp.daylightSavings.enable="1"')
            if tzinfo['dst']['start']['day'].startswith('D'):
                lines.append(u'tcpIpApp.sntp.daylightSavings.fixedDayEnable="1"')
            else:
                lines.append(u'tcpIpApp.sntp.daylightSavings.fixedDayEnable="0"')
            lines.extend(self._format_dst_change('start', tzinfo['dst']['start']))
            lines.extend(self._format_dst_change('stop', tzinfo['dst']['end']))
        return u'\n'.join(lines)
    
    def _gen_xx_timezone(self, raw_config):
        try:
            tzinfo = tzinform.get_timezone_info(raw_config.get(u'timezone'))
        except tzinform.TimezoneNotFoundError:
            return u''
        else:
            return self._format_tzinfo(tzinfo)
    
    def _gen_xx_language(self, raw_config):
        return self._XX_LANGUAGE_MAP.get(raw_config.get(u'locale'), u'')
    
    def _format_function_keys(self, funckeys, model):
        max_fkey_no = self._NB_FKEY_MAP.get(model, 0)
        lines = []
        for key_no, key in funckeys.iteritems():
            if key[u'supervision']:
                logger.warning('Polycom doesn\'t support non-supervised function keys')
            if key_no < 1 or key_no > max_fkey_no:
                logger.warning('Invalid function key no %s for Polycom %s -- must be in [1, %s[',
                               key_no, model, max_fkey_no)
            else:
                lines.append(u'attendant.resourceList.%s.address="%s"' % (key_no, key[u'exten']))
                lines.append(u'attendant.resourceList.%s.label="%s"' % (key_no, key[u'label']))
        return u'\n'.join(lines)
    
    def _gen_xx_fkeys(self, raw_config, model):
        return self._format_function_keys(raw_config[u'funckeys'], model)
    
    def _gen_xx_syslog_level(self, raw_config):
        if u'syslog' in raw_config:
            return self._XX_SYSLOG_LEVEL.get(raw_config[u'level'], self._XX_SYSLOG_LEVEL_DEF)
        else:
            return None
    
    def _gen_xx_sip_transport(self, raw_config):
        return self._XX_SIP_TRANSPORT.get(raw_config[u'sip'][u'transport'],
                                          self._XX_SIP_TRANSPORT_DEF)
    
    def _strip_pem_cert(self, pem_cert):
        # Remove the header/footer of a pem certificate and return only the
        # base64 encoded part of the certificate.
        return pem_cert.replace('\n', '')[len('-----BEGIN CERTIFICATE-----'):
                                          -len('-----END CERTIFICATE-----')]
    
    def _gen_xx_custom_cert(self, raw_config):
        if u'servers_root_and_intermediate_certificates' in raw_config[u'sip']:
            # Note that there's must be 1 and only 1 certificate in pem_cert,
            # i.e. list of certificates isn't accepted, but is not checked...
            pem_cert = raw_config[u'sip'][u'servers_root_and_intermediate_certificates']
            return self._strip_pem_cert(pem_cert)
        else:
            return None
    
    def _dev_specific_filename(self, device):
        # Return the device specific filename (not pathname) of device
        fmted_mac = format_mac(device[u'mac'], separator='')
        return '%s-user.cfg' % fmted_mac
    
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
        
        raw_config[u'XX_timezone'] = self._gen_xx_timezone(raw_config)
        raw_config[u'XX_language'] = self._gen_xx_language(raw_config)
        raw_config[u'XX_fkeys'] = self._gen_xx_fkeys(raw_config, device.get(u'model'))
        raw_config[u'XX_syslog_level'] = self._gen_xx_syslog_level(raw_config)
        raw_config[u'XX_sip_transport'] = self._gen_xx_sip_transport(raw_config)
        raw_config[u'XX_custom_cert'] = self._gen_xx_custom_cert(raw_config)
        
        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)
    
    def deconfigure(self, device):
        self._check_device(device)
        path = os.path.join(self._tftpboot_dir, self._dev_specific_filename(device))
        try:
            os.remove(path)
        except OSError, e:
            logger.warning('error while deconfiguring device: %s', e)
    
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
