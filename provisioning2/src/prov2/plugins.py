# -*- coding: UTF-8 -*-

from __future__ import with_statement

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

import ConfigParser
import contextlib
import os
import urllib2
import shutil
import tarfile
import tempfile
import fetchfw2.storage
import fetchfw2.package
from prov2.servers.tftp.service import TFTPNullService, TFTPFileService
from twisted.web.resource import NoResource
from twisted.web.static import File
from jinja2.loaders import FileSystemLoader, ChoiceLoader
from jinja2.environment import Environment
from fetchfw2.download import DefaultDownloader, AuthenticatingDownloader,\
    CiscoDownloader, NortelDownloader


# TODO quite a few methods are synchronous while they should be asynchronous
# TODO prise en compte des proxy pour téléchargement
# TODO répertoire de cache pour stocker les plugins ?
# TODO supporter la signature des plugins -- ca va etre important pour la sécurité,
#      comme les plugins ne sont pas sandboxer...


class Plugin(object):
    """Base class and entry point of every plugin.
    
    Here's some guideline every plugin should follow:
    
    When you have the choice, you SHOULD configure device to use HTTP instead
    of TFTP. HTTP requests have usually more information that can be used
    to identify device. HTTP is also faster (because of TFTP
    lock-step) and not limited in file size transfer. Since HTTP is based
    on TCP, it also usually play nicer with NAT, and in general, integrates
    better in complex network architecture.
    
    Keep in mind how new devices will interact with the
    plugin for the first time. For example, even if your plugin configure
    its device to use HTTP instead of TFTP, new device might have been
    configured to use TFTP before. This mean you should offer a TFTP service
    and TFTP identification even if you don't plan to make explicit use of
    it. That said, if your device support protocol selection from the DHCP
    server responses, this becomes less important.
    
    Similarly, keep in mind that you might interact with devices that are
    in a different version then what your plugin is targeting. Your plugin
    should try to recognize and accept these devices, at least the ones
    that are closely related. The plugin should then upgrade them in the
    targeted version of your plugin.
    
    Attributes:
    name -- the name of the plugin. This is set at plugin instantiation time
            if the plugin is created by the plugin manager
    _pluging_dir -- the base directory in which the plugin is
    _gen_cfg -- a read-only general configuration mapping object
    _spec_cfg -- a read-only plugin-specific configuration mapping object
    
    Plugin class that are made to be instantiated (i.e. the one doing the
    real job, and not superclass that helps it) must have an attribute
    'IS_PLUGIN' that evaluates to true in a boolean context or it won't be
    loaded. This is necessary to distinguish real plugin class from
    'helper' plugin superclasses. XXX This is ugly tough
    
    """
    name = None
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        self._plugin_dir = plugin_dir
        self._gen_cfg = gen_cfg
        self._spec_cfg = spec_cfg
    
    # Activation/deactivation methods
    
    # XXX useless for now, it does add some complexity (especially the deactivate part,
    # if we say something like it will always be called) but maybe it will be 
    # necessary for some plugin, 
    
    # useless -- idea state
    def activate(self):
        pass
    
    # useless -- idea state
    def deactivate(self):
        pass
    
    # Plugin configuration methods (called automatically)
    # XXX we'll probably want to move this method out of this class into a
    # separate class since we don't want to instantiate a plugin object before
    # configuring it
    
    def postinstall(self):
        """Called after a fresh install of the plugin."""
        pass
    
    # XXX useless -- idea state
    def preupgrade(self):
        pass
    
    # XXX useless -- idea state
    def postupgrade(self):
        pass
    
    # Methods for additional plugin services
    
    def services(self):
        """Retourne un mapping d'objets 'service' qui sont accessibles par
        ce plugin. Les clés sont les noms des services et les valeurs sont
        des objets services.
        
        Un service est un objet 'callable' avec un nombre quelconques
        d'arguments.
        
        TODO spécifier la signification de la valeur de retour d'un
        service, etc

        """
        return {}
    
    # Methods for TFTP/HTTP services
    
    def http_dev_info_extractors(self):
        """Return a potentially empty sequence of objects providing the
        IDeviceInfoExtractor interface for HTTP requests.
        
        In this case, request objects are twisted.web.http.Request objects.
        
        """
        return ()
    
    def http_service(self):
        """Return the HTTP service of this plugin.
        
        If not overridden, return a service that will answer every requets with a
        404 'not found' response.
        
        """
        return NoResource('Not found')
    
    def tftp_dev_info_extractors(self):
        """Return a potentially empty sequence of objects providing the
        IDeviceInfoExtractor interface for TFTP request.
        
        In this case, request objects are as defined in the
        prov2.servers.tftp.service module.
        
        """
        return ()
    
    def tftp_service(self):
        """Return the TFTP service of this plugin.
        
        If not overridden, return a service that will answer every requests with an
        ERROR 'file not found' response.
        
        """
        return TFTPNullService()
    
    def device_types(self):
        """Return a sequence of (vendor, model, version) tuple that this plugin explicitly
        supports.
        
        Useful if we want to do automatic device-plugin association.
        
        """
        return ()
    
    # Methods for device configuration
    
    # XXX - useful ? at the right place/right name ? 
    def configure_common(self, config):
        """Apply a non-device specific configuration to the plugin. In typical
        case, this will configure the 'common file' shared by all the devices.
        
        config is a mapping object with all the configurations parameters.
        Plugin class can modify this object.
        
        """ 
        pass
    
    # XXX should configure returns a deferred for flow control, that will fire
    #     once the configuration is done ?
    def configure(self, dev_info, config):
        """Apply a device specific configuration to a device.
        
        config is a mapping object with all the configurations parameters.
        Plugin class can modify this object.
        
        Raise an error if there's not enough information in dev_info.
        
        """
        pass
    
    def reload(self, dev_info, config):
        """Ask the device to reload its configuration files. This only
        applies to phone that uses configurations files (i.e. Siemens
        C470IP are excluded for example).
        
        Raise an error if the device can't not be asked to reload.
        
        """
        pass


class StandardPlugin(Plugin):
    """Plugin that helps with having a standardized plugin layout and
    which helps with repeating tasks, etc etc, this is a bad description.
    
    
    """
    # XXX is the name right ? StandardPhonePlugin ? StandardXivoPlugin ?
    TFTPBOOT_DIR = os.path.join('var', 'lib', 'tftpboot')
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        Plugin.__init__(self, plugin_dir, gen_cfg, spec_cfg)
        self._tftpboot_dir = os.path.join(plugin_dir, self.TFTPBOOT_DIR)
    
    def tftp_service(self):
        return TFTPFileService(self._tftpboot_dir)
    
    def http_service(self):
        return File(self._tftpboot_dir)


class TemplatePluginHelper(object):
    DEFAULT_TPL_DIR = 'templates'
    """Directory where the default templates lies."""
    CUSTOM_TPL_DIR = os.path.join('var', 'templates')
    """Directory where the custom templates lies."""
    
    def __init__(self, plugin_dir):
        custom_loader = FileSystemLoader(os.path.join(plugin_dir, self.CUSTOM_TPL_DIR))
        default_loader = FileSystemLoader(os.path.join(plugin_dir, self.DEFAULT_TPL_DIR))
        loader = ChoiceLoader((custom_loader, default_loader))
        self._env = Environment(trim_blocks=True, loader=loader)
        
    def get_template(self, name):
        return self._env.get_template(name)
    
    def dump(self, template, context, filename, encoding='UTF-8', errors='strict'):
        tmp_filename = filename + '.tmp'
        template.stream(context).dump(tmp_filename, encoding, errors)
        os.rename(tmp_filename, filename)


class FetchfwPluginHelper(object):
    """Helper for plugins that needs to download files to really
    be able to support a certain kind of device.
    
    """
    
    # TODO make the service asynchronous
    
    PKG_DIR = 'pkgs'
    """Directory where the package definitions are stored."""
    CACHE_DIR = os.path.join('var', 'cache')
    """Directory where the downloaded files are stored/cached."""
    INSTALLED_DIR = os.path.join('var', 'lib', 'installed')
    """Directory where the 'installed packages DB' is stored."""
    TFTPBOOT_DIR = os.path.join('var', 'lib', 'tftpboot')
    """Base directory where the files are extracted."""
    
    @staticmethod
    def _create_downloaders(http_proxy=None):
        supp_handlers = []
        if http_proxy:
            supp_handlers = urllib2.ProxyHandler({'http': http_proxy})
        default = DefaultDownloader(*supp_handlers)
        auth = AuthenticatingDownloader(*supp_handlers)
        cisco = CiscoDownloader(*supp_handlers)
        nortel = NortelDownloader(default)
        return {'default': default, 'auth': auth, 'cisco': cisco, 'nortel': nortel}
    
    def __init__(self, plugin_dir, http_proxy=None):
        self._plugin_dir = plugin_dir
        self.downloaders = self._create_downloaders(http_proxy)

        pkg_dir = os.path.join(plugin_dir, self.PKG_DIR)
        cache_dir = os.path.join(plugin_dir, self.CACHE_DIR)        
        installed_dir = os.path.join(plugin_dir, self.INSTALLED_DIR)
        doc_root = os.path.join(plugin_dir, self.TFTPBOOT_DIR)
        storage = fetchfw2.storage.DefaultPackageStorage(cache_dir, pkg_dir, installed_dir,
                                                         self.downloaders, {'DOC_ROOT': doc_root})
        self._pkg_manager = fetchfw2.package.PackageManager(storage)

#    def postinstall(self):
#        """Should be called when the plugin using this helper is installed. It creates
#        the three directories in var/.
#        
#        """
        # XXX currently, we have choosed to create these directory directly in
        # the filesystem in the plugin package
#        for rel_dir in [self.CACHE_DIR, self.INSTALLED_DIR, self.TFTPBOOT_DIR]:
#            abs_dir = os.path.join(self._plugin_dir, rel_dir)
#            try:
#                os.makedirs(abs_dir)
#            except OSError:
#                if not os.path.isdir(abs_dir):
#                    raise
#        pass
    
    
    def _install(self, *args):
        """Install the packages in args.
        
        args -- a sequence of package name to install
         
        """
        self._pkg_manager.install(args)
    
    def _uninstall(self, *args):
        """See _install."""
        self._pkg_manager.uninstall(args)
    
    def _list_installed(self):
        """Return the list (in the form of a generator) of installed package
        name.
        
        """
        self._pkg_manager.installed_pkgs.reload()
        return self._pkg_manager.installed_pkgs.iterkeys()

    def _list_installable(self):
        """See _list_installed."""
        return self._pkg_manager.installable_pkgs.iterkeys()
    
    def services(self):
        return {'install': self._install,
                'uninstall': self._uninstall,
                'list_installed': self._list_installed,
                'list_installable': self._list_installable}


class PluginManager(object):
    """Manage plugin installation and loading.
    
    A 'plugin info' object is a mapping object with the following keys:
      name -- the plugin name
      version -- the plugin version (not to mistake with the version 
                of the device the plugin supports)
    
    An 'installable plugin info' is a 'plugin info' object + the following keys:
      filename -- the name of the file to download on the remote server (i.e.
                  the name of the plugin package)
    
    """
    
    _DEF_FILENAME = 'defs'
    """The plugin definition filename on the remote and local server."""
    _INFO_FILENAME = 'plugin-info'
    """The name of the plugin information file."""
    _ENTRY_FILENAME = 'entry.py'
    """The name of the python plugin code."""
    
    def __init__(self, plugins_dir, server):
        """
        plugins_dir -- the directory where plugins are installed
        server -- a partial URL of the server where to download plugins and plugins definition
        
        """
        self._plugins_dir = plugins_dir
        self._server = server
    
    def _def_pathname(self):
        return os.path.join(self._plugins_dir, self._DEF_FILENAME)
    
    def _join_server_url(self, p):
        if self._server.endswith('/'):
            return self._server + p
        else:
            return self._server + '/' + p
    
    def _install_plugin(self, plugin):
        url = self._join_server_url(plugin['filename'])
        with tempfile.TemporaryFile() as fdst:
            with contextlib.closing(urllib2.urlopen(url)) as fsrc:
                shutil.copyfileobj(fsrc, fdst)
            
            fdst.seek(0)
            tfile = tarfile.open(name=plugin['filename'], fileobj=fdst)
            # XXX this is unsafe unless we have authenticated the tarfile
            tfile.extractall(self._plugins_dir)
    
    def install(self, name):
        """Install a plugin.
        
        Do not check if the plugin is already installed
        
        """
        for plugin in self.list_installable():
            if plugin['name'] == name:
                break
        else:
            raise ValueError('plugin not found')
        
        self._install_plugin(plugin)
        
    def uninstall(self, name):
        """Uninstall a plugin.
        
        Do not check if some devices used this plugin.
        
        """
        for plugin in self.list_installed():
            if plugin['name'] == name:
                break
        else:
            raise ValueError('plugin not found')
        
        shutil.rmtree(os.path.join(self._plugins_dir, name))
    
    def update(self):
        """Download the plugin definition file from the remote server.
        
        Return when the transfer is complete or throws an exception.
        
        """
        url = self._join_server_url(self._DEF_FILENAME)
        # TODO this is a non atomic operation and might fail and leave our
        #      stuff in an inconsitent state
        with open(self._def_pathname(), 'w') as fdst:
            with contextlib.closing(urllib2.urlopen(url)) as fsrc:
                shutil.copyfileobj(fsrc, fdst)
        
    def upgrade(self):
        """Upgrade all the packages that can be upgraded."""
        installed = dict((plugin['name'], plugin['version']) for plugin in
                         self.list_installed())
        # XXX the version comparison is cheap
        upgradable = (plugin for plugin in self.list_installable() if
                      plugin['name'] in installed and 
                      plugin['version'] > installed.get(plugin['name'], ''))
        for plugin in upgradable:
            self._install_plugin(plugin)
    
    def list_installable(self):
        """Return the information on the installable plugins as a generator."""
        config = ConfigParser.RawConfigParser()
        with open(self._def_pathname(), 'r') as fobj:
            config.readfp(fobj)
        
        for section in config.sections():
            if not section.startswith('plugin_'):
                raise ValueError('invalid plugin definition file')
            name = section[len('plugin_'):]
            filename = config.get(section, 'filename')
            version = config.get(section, 'version')
            yield {'name': name, 'filename': filename, 'version': version}
        
    def list_installed(self):
        """Return the information on the installed plugins as a generator."""
        for rel_plugin_dir in os.listdir(self._plugins_dir):
            abs_plugin_dir = os.path.join(self._plugins_dir, rel_plugin_dir)
            if os.path.isdir(abs_plugin_dir):
                info_pathname = os.path.join(abs_plugin_dir, self._INFO_FILENAME)
                with open(info_pathname, 'r') as fobj:
                    config = ConfigParser.ConfigParser()
                    config.readfp(fobj)
                version = config.get('general', 'version')
                yield {'name': rel_plugin_dir, 'version': version}

    def load(self, name, gen_cfg={}, spec_cfg={}):
        """Load a plugin and return an instance of it."""
        # XXX raise some kind of meaningful exception if there's some kind of error
        plugin_dir = os.path.join(self._plugins_dir, name)
        py_file = os.path.join(plugin_dir, self._ENTRY_FILENAME)
        plugin_globals = {}
        execfile(py_file, plugin_globals)
        for el in plugin_globals.itervalues():
            if (isinstance(el, type) and 
                issubclass(el, Plugin) and
                hasattr(el, 'IS_PLUGIN') and
                getattr(el, 'IS_PLUGIN')):
                    plugin = el(plugin_dir, gen_cfg, spec_cfg)
                    plugin.name = name
                    return plugin
        else:
            raise ValueError('no plugin class found in file')

    def load_all(self, gen_cfg={}, spec_cfg={}):
        """Load all the installed plugins and return a generator yielding plugin instances."""
        # spec_cfg is a mapping which keys are plugin name and which values are
        # specific configuration mapping for the plugin with this name
        for pg_info in self.list_installed():
            pg_name = pg_info['name']
            yield self.load(pg_name, gen_cfg, spec_cfg.get(pg_name, {}))

