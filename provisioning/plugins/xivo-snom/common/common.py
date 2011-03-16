# -*- coding: UTF-8 -*-

"""Plugin for Snom 300, 320, 360, 370, 820, 821 and 870 in version 8.4.18."""

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
from provd import tzinform
from provd.devices.pgasso import BasePgAssociator, IMPROBABLE_SUPPORT,\
    PROBABLE_SUPPORT, FULL_SUPPORT, NO_SUPPORT, COMPLETE_SUPPORT,\
    INCOMPLETE_SUPPORT
from provd.plugins import StandardPlugin, FetchfwPluginHelper,\
    TemplatePluginHelper
from provd.util import norm_mac, format_mac
from twisted.internet import defer
from twisted.web.resource import Resource
from twisted.web.static import Data, File


class BaseSnomHTTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    _UA_REGEX = re.compile(r'\bsnom([\w]+)-SIP ([\w.]+)')
    _FILENAME_REGEX = re.compile(r'\b([\dA-F]{12})\b')
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = {}
            self._extract_from_ua(ua, dev_info)
            if dev_info:
                dev_info['vendor'] = 'Snom'
                filename = request.path
                self._extract_from_filename(filename, dev_info)
                return dev_info
    
    def _extract_from_ua(self, ua, dev_info):
        # HTTP User-Agent:
        #   "Mozilla/4.0 (compatible; snom lid 3605)" --> Snom 6.5.xx
        #   "Mozilla/4.0 (compatible; snom320-SIP 6.5.20; snom320 jffs2 v3.36; snom320 linux 3.38)"
        #   "Mozilla/4.0 (compatible; snom320-SIP 7.3.30 1.1.3-u)"
        #   "Mozilla/4.0 (compatible; snom320-SIP 8.4.18 1.1.3-s)"
        #   "Mozilla/4.0 (compatible; snom820-SIP 8.4.18 1.1.4-IFX-26.11.09)"
        #   "Mozilla/4.0 (compatible; snom870-SIP 8.3.6 SPEAr300 SNOM 1.4)"
        #   "Mozilla/4.0 (compatible; snom870-SIP 8.4.18 SPEAr300 SNOM 1.4)"
        m = self._UA_REGEX.search(ua)
        if m:
            dev_info['model'], dev_info['version'] = m.groups()
    
    def _extract_from_filename(self, filename, dev_info):
        m = self._FILENAME_REGEX.search(filename)
        if m:
            dev_info['mac'] = norm_mac(m.group(1))


class BaseSnomPgAssociator(BasePgAssociator):
    def __init__(self, models, version, compat_models):
        self._models = models
        self._version = version
        self._compat_models = compat_models
        
    def _do_associate(self, vendor, model, version):
        if vendor == 'Snom':
            if version is None:
                # Could be an old version with no XML support
                return PROBABLE_SUPPORT
            assert version is not None
            if self._is_incompatible_version(version):
                return NO_SUPPORT
            if model in self._models:
                if version == self._version:
                    return FULL_SUPPORT
                return COMPLETE_SUPPORT
            if model in self._compat_models:
                return INCOMPLETE_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT
    
    def _is_incompatible_version(self, version):
        """
        Pre: model is not None
             version is not None
        """
        # XXX if we support snom m3 one day, this will need to be
        #     changed or overriden... or if we add support for an
        #     old (6) firmware to enable automatic upgrade...
        try:
            maj_version = int(version[0])
            if maj_version < 7:
                return True
        except (IndexError, ValueError):
            pass
        return False


class BaseSnomHTTPService(Resource):
    # XXX note that if we use common configuration, this could be removed
    """Dynamic and static HTTP service."""
    
    def __init__(self, snom_pg):
        Resource.__init__(self)
        self._app = snom_pg._app
        self._tpl_helper = snom_pg._tpl_helper
        self._service = File(snom_pg._tftpboot_dir)
        self._encoding = snom_pg._ENCODING
    
    def _static_render(self, path, request):
        resrc = self._service
        if resrc.isLeaf:
            request.postpath.insert(0, request.prepath.pop())
            return resrc
        else:
            return resrc.getChildWithDefault(path, request)
    
    def getChild(self, path, request):
        # XXX that makes me think, how good will it handle the load, for
        # example, after a power failure, if a large amount of phones
        # reboot at the same time
        # we do not render the base.xxx.tpl -- these are generated per request
        if not path.startswith('base'):
            dev = request.prov_dev
            if dev and 'config' in dev:
                try:
                    tpl = self._tpl_helper.get_template(path + '.tpl')
                except TemplateNotFound:
                    pass
                else:
                    config = self._app.retrieve_cfg(dev['config'])
                    content = self._tpl_helper.render(tpl, config, self._encoding)
                    return Data(content, 'application/xml')
        return self._static_render(path, request)


class BaseSnomPlugin(StandardPlugin):
    _ENCODING = 'UTF-8'
    _XX_LANG = {
        'de_DE': ('Deutsch', 'GER'),
        'en_US': ('English', 'USA'),
        'es_ES': ('Espanol', 'ESP'),
        'fr_FR': ('Francais', 'FRA'),
        'fr_CA': ('Francais', 'USA'),
    }
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        rfile_builder = FetchfwPluginHelper.new_rfile_builder(gen_cfg.get('proxies'))
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        self.services = self._fetchfw_helper.services()
        self.http_service = BaseSnomHTTPService(self)
    
    http_dev_info_extractor = BaseSnomHTTPDeviceInfoExtractor()
    
    def _get_xx_fkeys(self, config):
        funckey = config['funckey']
        proxy_ip = config['sip'][0]['proxy_ip']
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
    
    def _get_xx_lang(self, config):
        if 'locale' in config:
            return self._XX_LANG.get(config['locale'])
    
    def _format_dst_change(self, dst_change):
        fmted_time = '%02d:%02d:%02d' % tuple(dst_change['time'].as_hms)
        day = dst_change['day']
        if day.startswith('D'):
            return '%02d.%02d %s' % (int(day[1:]), dst_change['month'], fmted_time)
        else:
            week, weekday = map(int, day[1:].split('.'))
            weekday = tzinform.week_start_on_monday(weekday)
            return '%02d.%02d.%02d %s' % (dst_change['month'], week, weekday, fmted_time)
    
    def _get_xx_timezone(self, config):
        inform = tzinform.get_timezone_info(config['timezone'])
        lines = []
        lines.append('<timezone perm="R"></timezone>')
        lines.append('<utc_offset perm="R">%+d</utc_offset>' % inform['utcoffset'].as_seconds)
        if inform['dst'] is None:
            lines.append('<dst perm="R"></dst>')
        else:
            lines.append('<dst perm="R">%d %s %s</dst>' % 
                         (inform['dst']['save'].as_seconds,
                          self._format_dst_change(inform['dst']['start']),
                          self._format_dst_change(inform['dst']['end'])))
        return '\n'.join(lines)
    
    def _dev_specific_filename(self, fmted_mac):
        return fmted_mac + '.xml'
    
    def configure(self, dev, config):
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        filename = self._dev_specific_filename(fmted_mac)
        tpl = self._tpl_helper.get_dev_template(filename, dev)
        
        config['XX_fkeys'] = self._get_xx_fkeys(config)
        config['XX_lang'] = self._get_xx_lang(config)
        config['XX_timezone'] = self._get_xx_timezone(config)
        
        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, config, path, self._ENCODING)
        
        # generate the intermediary 'redirect' file
        redir_filename = '%s.htm' % fmted_mac
        redir_tpl = self._tpl_helper.get_template('base.htm.tpl')
        config['XX_mac'] = fmted_mac
        redir_path = os.path.join(self._tftpboot_dir, redir_filename)
        self._tpl_helper.dump(redir_tpl, config, redir_path, self._ENCODING)
    
    def deconfigure(self, dev):
        fmted_mac = format_mac(dev['mac'], separator='', uppercase=True)
        filename = self._dev_specific_filename(fmted_mac)
        os.remove(os.path.join(self._tftpboot_dir, filename))
    
    def synchronize(self, dev, config):
        # TODO
        pass
