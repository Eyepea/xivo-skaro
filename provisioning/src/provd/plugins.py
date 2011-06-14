# -*- coding: UTF-8 -*-

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

# TODO support plugin package signing... this will be important for safety
#      since plugin aren't sandboxed

import contextlib
import json
import logging
import os
import shutil
import tarfile
import urlparse
import weakref
from binascii import a2b_hex
from fetchfw.download import new_downloaders, DefaultDownloader, RemoteFile,\
    SHA1Hook
from fetchfw.package import DefaultInstaller, PackageManager
from fetchfw.storage import RemoteFileBuilder, InstallationMgrBuilder,\
    DefaultPackageStorage
from provd.download import async_download_multiseq_with_oip,\
    async_download_with_oip
from provd.loaders import ProvdFileSystemLoader
from provd.operation import OperationInProgress, OIP_PROGRESS, OIP_SUCCESS,\
    OIP_FAIL
from provd.proxy import DynProxyHandler
from provd.services import AttrConfigureServiceParam, BaseConfigureService,\
    IInstallService, InvalidParameterError, JsonConfigPersister,\
    PersistentConfigureServiceDecorator, DictConfigureServiceParam
from jinja2.environment import Environment
from jinja2.exceptions import TemplateNotFound
from twisted.internet import defer
from zope.interface import implements, Interface

logger = logging.getLogger(__name__)


_PLUGIN_INFO_FILENAME = 'plugin-info'
# plugin information filename in each plugin directory.
_PLUGIN_INFO_KEYS = [u'capabilities', u'description', u'version']
_PLUGIN_INFO_INSTALLABLE_KEYS = _PLUGIN_INFO_KEYS + [u'dsize', u'filename', u'sha1sum']
_PLUGIN_INFO_INSTALLED_KEYS = _PLUGIN_INFO_KEYS

def _check_raw_plugin_info(raw_plugin_info, id, keys):
    # Quick and incomplete check of a raw plugin info object.
    for plugin_info_key in keys:
        if plugin_info_key not in raw_plugin_info:
            raise ValueError('invalid plugin info: missing %s key in %s'
                             % (plugin_info_key, id))


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
    id -- the ID of the plugin. This attribute is set after the plugin
          instantiation time by the plugin manager
    services
    http_dev_info_extractor
    http_service
    tftp_dev_info_extractor
    tftp_service
    
    Plugin class that are made to be instantiated (i.e. the one doing the
    real job, and not superclass that helps it) must have an attribute
    'IS_PLUGIN' that evaluates to true in a boolean context or it won't be
    loaded. This is necessary to distinguish real plugin class from
    'helper' plugin superclasses. XXX This is ugly tough
    
    At load time, the 'execfile_' name is available in the global namespace
    of the entry file. It can be used to 'import' other files in the same or
    sub directory of the entry plugin file. This methods is similar to
    execfile, except that the working directory is changed to the plugin
    directory.
    
    """
    id = None
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        """Create a new plugin instance.
        
        This method is the first method called in the plugin loading process.
        
        The application guarantees that there will never be more than 1 'active'
        plugin instance at the same time for a same plugin. An instance is
        active between the time of its creation and the time its close method
        is called.
        
        app -- the application object
        plugin_dir -- the root directory where the plugin lies
        gen_cfg -- a dictionary with generic configuration key-values
            XXX should specify better
        spec_cfg --  a dictionary with plugin-specific configuration key-values
            XXX should specify better
        
        """
        self._plugin_dir = plugin_dir
    
    def close(self):
        """Close the plugin.
        
        This method is the last method called in the plugin unloading process.
        
        In normal situation, this method is guaranteed to be the last one
        called in the life-cycle of a plugin instance, and may not be called
        more than once.
        
        """
        pass
    
    def info(self):
        """Return a dictionary containing information about this plugin.
        
        The dictionary MUST contains at least the following keys:
          version -- the version of the plugin
          description -- the description of the plugin
          capabilities -- a dictionary where keys are string in format
            "vendor, model, version" and values are capabilities dictionary.
        
        Note that the returned dictionary contains unicode strings.
        
        Raise an Exception if the plugin information is missing or invalid.
        
        """
        plugin_info_path = os.path.join(self._plugin_dir, _PLUGIN_INFO_FILENAME)
        with open(plugin_info_path) as fobj:
            raw_plugin_info = json.load(fobj)
        _check_raw_plugin_info(raw_plugin_info, self.id, _PLUGIN_INFO_INSTALLED_KEYS)
        return raw_plugin_info
    
    # Methods for additional plugin services
    
    services = {}
    """Return a dictionary where keys are service name and values are
    service object.
    
    This is used so that plugins can offer additional services in a
    standard way.
    
    If the service name is 'configure', the associated service object must
    provide the IConfigureService interface.
    
    If the service name is 'install', the associated service object must
    provide the IInstallService interface.
    
    """
    
    # Methods for TFTP/HTTP services
    
    # Contrary to TFTP and HTTP, there's no DHCP service, but only an extractor
    dhcp_dev_info_extractor = None
    """An object providing the IDeviceInfoExtractor interface for DHCP
    requests or None if there's no such object.
    
    """
    
    http_dev_info_extractor = None
    """An object providing the IDeviceInfoExtractor interface for HTTP
    requests or None if there's no such object.
    
    """
    
    http_service = None
    """The HTTP service of this plugin, or None if the plugin doesn't offer
    an HTTP service.
    
    Note that the request objects passed to the render method of this service
    have a 'prov_dev' attribute set to the device object representing the
    device which is doing the request, or None if the device is unknown.
    
    """
    
    tftp_dev_info_extractor = None
    """An object providing the IDeviceInfoExtractor interface for TFTP
    request or None if there's no such object.
    
    """

    tftp_service = None
    """The TFTP service of this plugin, or None if the plugin
    doesn't offer a TFTP service.
    
    Note that the request objects passed to the handle_read_request method of
    this service have a 'prov_dev' key set to the device object representing
    the device which is doing the request, or None if the device is unknown.
    
    """
    
    pg_associator = None
    """Return an object providing the IPluginAssociator interface, or None if
    the plugin doesn't have a plugin associator.
    
    """
    
    # Methods for device configuration
    
    def configure_common(self, raw_config):
        """Apply a non-device specific configuration to the plugin. In typical
        case, this will configure the 'common files' shared by all the devices.
        
        This method is called automatically the first time an installed plugin
        is loaded, and also called when there's a change to the common config.
        Note that this method might also be called more often than
        technically needed.
        
        raw_config is a raw config object with all the common configurations
        parameters. An 'ip', 'http_port' and 'tftp_port' parameters are
        guaranteed to be present. Plugin class can modify this object.
        
        This method is synchronous/blocking.
        
        """ 
        pass
    
    def configure(self, device, raw_config):
        """Configure the plugin so that the raw config is applied to the
        device. This method MUST not synchronize the configuration between
        the phone and the provisioning server. This method is called only to
        synchronize the config between the config manager and the plugin. See
        the synchronize method for more info on the device configuration life cycle. 
        
        This method is called in these cases:
        - a device object with a config associated to it has been assigned
          to this plugin
        - the config object used by a device has been updated
        - one of the mac, ip, vendor, model or version key of a device object
          managed by this plugin has been updated
        
        This method is mostly useful for 'pull type' plugins, especially static
        pull type plugin. For these plugin, this is the right time to write the
        device specific configuration file to the filesystem. This makes sure
        the config inside the device specific configuration file is in sync
        with the config object from the config manager.
        
        Pre:  device is a device object (can't be None)
              raw_config is a raw config object (can't be None). The plugin
                is free to modify this object (it won't affect anything).
                The meaning of the value in the config object are defined in
                the config module.
        Post: after a call to this method, if the device does a request for
                its configuration file, its configuration will be as the
                config object
        
        Plugin class can modify the raw_config object.
        
        This method is synchronous/blocking.
        
        """
        pass
    
    def deconfigure(self, device):
        """Deconfigure the plugin so that the plugin won't configure the
        device.
        
        This method is called when:
        - a device is changed from this plugin to another plugin
        - a device is going to be deleted
        - the config has been deleted from a device (i.e. no more 'config' key)
        
        This method is mostly useful for 'pull type' plugins, especially
        static pull type plugins. This is the right time to delete any device
        specific configuration related to the device. This is to prevent
        unexpected configuration for a device and to keep the plugins
        clean, without out of sync cache file in their directories.
        
        Note that deconfigure doesn't mean you should try resetting the
        device to its default value. In fact, you SHOULD NOT do this.
        
        In some rare circumstances, this method might be called more than
        once for the same device object, so plugin should be prepared to
        such eventuality.
        
        Pre:  device is a device object
              the method 'configure' has been called at least once with the
                same device object since the last call to deconfigure with
                the same device (i.e. a call to deconfigure can only follow
                a call to the configure method with the same device, and there
                must not be a call to deconfigure between these 2 calls)
        Post: after a call to this method, if device dev does a request for
                its configuration file, it won't be configured with an old
                config (it's ok if the device is configured with the common
                configuration though)
        
        This method is synchronous/blocking.
        
        """
        pass
    
    def synchronize(self, device, raw_config):
        """Force the device to synchronize its configuration so that its the
        same as the one in the raw config object.
        
        Note that an offline device can't be synchronized...
        
        Pre:  device is a device object (can't be None)
              raw_config is a raw config object (can't be None)
              there has been no change to the config object since the last
                call to the configure method with the same device object and
                config object. Said differently, before this call, there has
                been a call to configure with the same object, and there has
                been no call to deconfigure with the same dev object between
                these calls and no other call to configure with the same dev
                object.
        Post: its config has been reloaded
        
        Plugin class can modify the raw_config object.
        
        Return a Deferred that fire with None if the resync seems to have
        been successful.
        
        The deferred will fire its errback with an Exception in the following
        case:
          - resynchronization is not supported by this plugin.
          - not enough information to resynchronize the device.
          - the resync operation seems to have failed for another reason.
        
        """
        return defer.fail(Exception("Resynchronization not supported"))


class StandardPlugin(Plugin):
    """Abstract base class for plugin classes.
    
    Altough this class doesn't do much at the time of writing this, you'll
    still want to inherit from it, unless you have good reason.
    
    """
    _TFTPBOOT_DIR = os.path.join('var', 'tftpboot')
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        Plugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        self._tftpboot_dir = os.path.join(plugin_dir, self._TFTPBOOT_DIR)


class TemplatePluginHelper(object):
    DEFAULT_TPL_DIR = 'templates'
    """Directory where the default templates lies."""
    CUSTOM_TPL_DIR = os.path.join('var', 'templates')
    """Directory where the custom templates lies."""
    
    def __init__(self, plugin_dir):
        custom_dir = os.path.join(plugin_dir, self.CUSTOM_TPL_DIR)
        default_dir = os.path.join(plugin_dir, self.DEFAULT_TPL_DIR)
        loader = ProvdFileSystemLoader([custom_dir, default_dir])
        self._env = Environment(loader=loader)
    
    def get_dev_template(self, filename, dev):
        """Get the device template used for the device specific configuration
        file.
        
        """
        # XXX not sure device that device specific template should have the
        #     form 'filename' + '.tpl'...
        # get device-specific template
        if filename:
            logger.info('Getting device specific template')
            try:
                return self._env.get_template(filename + '.tpl')
            except TemplateNotFound:
                logger.info('Device specific template not found.')
        else:
            logger.info('No device specific information available for device.')
        # get model-specific template
        if 'model' in dev:
            logger.info('Getting model specific template')
            model = dev['model']
            try:
                return self._env.get_template(model + '.tpl')
            except TemplateNotFound:
                logger.info('Model specific template not found.')
        else:
            logger.info('No model information available for device.')
        # get base template
        logger.info('Getting base template')
        return self._env.get_template('base.tpl')
    
    def get_template(self, name):
        return self._env.get_template(name)
    
    def dump(self, template, context, filename, encoding='UTF-8', errors='strict'):
        logger.info('Writing template to file "%s"', filename)
        tmp_filename = filename + '.tmp'
        template.stream(context).dump(tmp_filename, encoding, errors)
        os.rename(tmp_filename, filename)
    
    def render(self, template, context, encoding='UTF-8', errors='strict'):
        return template.render(context).encode(encoding, errors)

        
class _AsyncPackageManager(PackageManager):
    """Custom async package manager. The interface of the install and upgrade
    method is a bit different from the standard PackageManager.
    
    """
    
    def __init__(self, pkg_storage):
        PackageManager.__init__(self, pkg_storage)
    
    def install(self, pkg_id):
        """Install a package and return a tuple (deferred, operation in progress)."""
        return _async_install([pkg_id], self._installable_pkgs,
                              self._installed_pkgs)
    
    def upgrade(self, pkg_id):
        raise NotImplementedError('async version not implemented because not needed')


def _async_install(pkg_ids, installable_pkgs, installed_pkgs):
    # XXX DefaultInstaller doesn't play nice with async code. In fact, we
    #     would like to review it, but there's higher priority...
    installer = DefaultInstaller()
    clean_pkg_names = installer._clean_pkg_names(pkg_ids, installable_pkgs, installed_pkgs)
    to_install_pkgs = installer._get_pkgs_to_install(clean_pkg_names, installable_pkgs, installed_pkgs)
    installer._pre_download(to_install_pkgs)
    # download the files
    # take extra step to make sure we won't download the same file twice
    rfiles = []
    rfiles_path = set()
    for to_install_pkg in to_install_pkgs:
        for rfile in to_install_pkg.remote_files:
            if not rfile.exists() and rfile.path not in rfiles_path:
                rfiles.append(rfile)
                rfiles_path.add(rfile.path)
    dl_deferred, dl_oip = async_download_multiseq_with_oip(rfiles)
    dl_oip.label = 'download'
    # create operation in progress objects
    # Note: important to create it these objects else the callback might
    # fire and the name not set
    install_oip = OperationInProgress('install')
    oip = OperationInProgress('install_pkg', OIP_PROGRESS,
                              sub_oips=[dl_oip, install_oip])
    deferred = defer.Deferred()
    def dl_success(_):
        install_oip.state = OIP_PROGRESS
        try:
            installer._pre_install(to_install_pkgs)
            new_pkgs = installer._install(to_install_pkgs)
            installer._post_install(new_pkgs)
            # step normally done in package manager -- update installed_pkgs
            for new_pkg in new_pkgs:
                installed_pkgs[new_pkg.name] = new_pkg
            installed_pkgs.flush()
        except Exception, e:
            install_oip.state = OIP_FAIL
            oip.state = OIP_FAIL
            deferred.errback(e)
        else:
            # fire callback
            install_oip.state = OIP_SUCCESS
            oip.state = OIP_SUCCESS
            deferred.callback(None)
    def dl_fail(err):
        install_oip.state = OIP_FAIL
        oip.state = OIP_FAIL
        deferred.errback(err)
    dl_deferred.addCallbacks(dl_success, dl_fail)
    return (deferred, oip)


def _new_handlers(proxies=None):
    if proxies is None:
        handlers = []
    else:
        handlers = [DynProxyHandler(proxies)]
    return handlers


class FetchfwPluginHelper(object):
    """Helper for plugins that needs to download files to really
    be able to support a certain kind of device.
    
    """
    
    implements(IInstallService)
    
    PKG_DIR = 'pkgs'
    """Directory where the package definitions are stored."""
    CACHE_DIR = os.path.join('var', 'cache')
    """Directory where the downloaded files are stored/cached."""
    INSTALLED_DIR = os.path.join('var', 'installed')
    """Directory where the 'installed packages DB' is stored."""
    TFTPBOOT_DIR = os.path.join('var', 'tftpboot')
    """Base directory where the files are extracted."""
    
    @classmethod
    def new_handlers(cls, proxies=None):
        return _new_handlers(proxies)
    
    @classmethod
    def new_rfile_builder(cls, proxies=None):
        downloaders = new_downloaders(_new_handlers(proxies))
        return RemoteFileBuilder(downloaders)
    
    def __init__(self, plugin_dir, rfile_builder=None, installation_mgr_builder=None):
        self._plugin_dir = plugin_dir
        if rfile_builder is None:
            rfile_builder = self.new_rfile_builder()
        if installation_mgr_builder is None:
            installation_mgr_builder = InstallationMgrBuilder()

        pkg_dir = os.path.join(plugin_dir, self.PKG_DIR)
        cache_dir = os.path.join(plugin_dir, self.CACHE_DIR)        
        installed_dir = os.path.join(plugin_dir, self.INSTALLED_DIR)
        doc_root = os.path.join(plugin_dir, self.TFTPBOOT_DIR)
        storage = DefaultPackageStorage(cache_dir, pkg_dir, installed_dir,
                                        rfile_builder, installation_mgr_builder,
                                        {'DOC_ROOT': doc_root})
        self._async_pkg_manager = _AsyncPackageManager(storage)
        self._in_install_set = set()
    
    def install(self, pkg_id):
        """Install a package.
        
        See IInstallService.install.
        
        """
        logger.info('Installing plugin-package %s', pkg_id)
        if pkg_id in self._in_install_set:
            raise Exception('an install operation for pkg %s is already in progress' % pkg_id)
        if pkg_id not in self._async_pkg_manager.installable_pkgs:
            raise Exception('package not found')

        # FIXME right now, it's possible to have 2 download for the same
        #       file at the same time, which would lead to some bad things
        #       We could mitigate this by using a remote file object that
        #       download to an arbitrarly name file before renaming, so we
        #       could have 2 download of the same file at the same time with
        #       I believe no consequence
        deferred, oip = self._async_pkg_manager.install(pkg_id)
        self._in_install_set.add(pkg_id)
        def on_success_or_error(v):
            self._in_install_set.remove(pkg_id)
            return v
        deferred.addBoth(on_success_or_error)
        return deferred, oip
    
    def uninstall(self, pkg_id):
        """Uninstall a package.
        
        See IInstallService.uninstall.
        
        """
        logger.info('Uninstalling plugin-package %s', pkg_id)
        self._async_pkg_manager.uninstall((pkg_id,))

    def list_installable(self):
        """Return a dictionary of installable packages.
        
        See IInstallService.list_installable.
        
        """
        installable_pkgs = self._async_pkg_manager.installable_pkgs
        return dict((pkg_id, {'version': pkg.version,
                              'description': pkg.description,
                              'dsize': sum(rfile.size for rfile in pkg.remote_files)})
                    for pkg_id, pkg in installable_pkgs.iteritems())
    
    def list_installed(self):
        """Return a dictionary of installed packages.
        
        See IInstallService.list_installed.
        
        """
        installed_pkgs = self._async_pkg_manager.installed_pkgs
        installed_pkgs.reload()
        return dict((pkg_id, {'version': pkg.version,
                              'description': pkg.description})
                    for pkg_id, pkg in installed_pkgs.iteritems())
    
    def services(self):
        """Return the following dictionary: {'install': self}."""
        return {'install': self}


class IPluginManagerObserver(Interface):
    """Interface that objects which want to be notified of plugin
    loading/unloading MUST provide.
    
    """
    def pg_load(pg_id):
        pass
    
    def pg_unload(pg_id):
        pass


class BasePluginManagerObserver(object):
    # Warning: don't forget to store at least 1 reference to this object
    # after attaching it to the plugin manager since observers are weakly
    # referenced by the plugin manager, so if you do not store any reference,
    # the observer will be automatically garbage collected
    def __init__(self, pg_load=None, pg_unload=None):
        self._pg_load = pg_load
        self._pg_unload = pg_unload
    
    def pg_load(self, pg_id):
        if self._pg_load is not None:
            self._pg_load(pg_id)
    
    def pg_unload(self, pg_id):
        if self._pg_unload is not None:
            self._pg_unload(pg_id)


def _check_is_server_url(value):
    if value is None:
        return
    
    try:
        parse_result = urlparse.urlparse(value)
    except Exception, e:
        raise InvalidParameterError(e)
    else:
        if not parse_result.scheme:
            raise InvalidParameterError('no scheme: %s' % value)
        if not parse_result.hostname:
            raise InvalidParameterError('no hostname: %s' % value)


def _check_is_proxy(value):
    if value is None:
        return
    
    try:
        parse_result = urlparse.urlparse(value)
    except Exception, e:
        raise InvalidParameterError(e)
    else:
        if not parse_result.scheme:
            raise InvalidParameterError('no scheme: %s' % value)
        if not parse_result.hostname:
            raise InvalidParameterError('no hostname: %s' % value)
        if parse_result.path:
            raise InvalidParameterError('path: %s' % value)


def _check_is_https_proxy(value):
    if value is None:
        return
    
    try:
        parse_result = urlparse.urlparse(value)
    except Exception, e:
        raise InvalidParameterError(e)
    else:
        if parse_result.scheme and parse_result.hostname:
            raise InvalidParameterError('scheme and hostname: %s' % value)


class PluginManager(object):
    """Manage the life cycle of plugins in the plugin ecosystem.
    
    Plugin manager objects have a 'server' attribute which represent the base
    address of the plugins repository (ex.: http://www.example.com/provd/stable).
    It can be set to None if no server is specified.
    
    """
    
    _ENTRY_FILENAME = 'entry.py'
    # name of the python plugin code
    _DB_FILENAME = 'plugins.db'
    # plugin definition filename on the remote and local server.
    
    _INSTALL_LABEL = 'install'
    _DOWNLOAD_LABEL = 'download'
    _UPDATE_LABEL = 'update'
    
    def __init__(self, app, plugins_dir, cache_dir):
        """
        app -- a provisioning application object
        plugins_dir -- the directory where plugins are installed
        cache_dir -- a directory where plugin-package are downloaded
        """
        self._app = app
        self._plugins_dir = plugins_dir
        self._cache_dir = cache_dir
        self.server = None
        proxies = app.proxies
        server_p = AttrConfigureServiceParam(self, 'server',
                                             u'The base address of the plugins repository',
                                             _check_is_server_url)
        http_proxy_p = DictConfigureServiceParam(proxies, 'http',
                                                 u'The proxy for HTTP requests. Format is "http://[user:password@]host:port"',
                                                 _check_is_proxy)
        ftp_proxy_p = DictConfigureServiceParam(proxies, 'ftp',
                                                u'The proxy for FTP requests. Format is "http://[user:password@]host:port"',
                                                _check_is_proxy)
        # syntax for specifying the HTTPS proxy is a bit different, don't ask me why
        https_proxy_p = DictConfigureServiceParam(proxies, 'https',
                                                  u'The proxy for HTTPS requests. Format is "host:port"',
                                                  _check_is_https_proxy)
        cfg_service = BaseConfigureService({u'server': server_p,
                                            u'http_proxy': http_proxy_p,
                                            u'ftp_proxy': ftp_proxy_p,
                                            u'https_proxy': https_proxy_p})
        persister = JsonConfigPersister(os.path.join(plugins_dir, 'config.json'))
        self._cfg_service = PersistentConfigureServiceDecorator(cfg_service, persister)
        self._in_update = False
        self._in_install = set()
        self._observers = weakref.WeakKeyDictionary()
        self._plugins = {}
        self._downloader = DefaultDownloader(_new_handlers(proxies))
    
    def close(self):
        """Close the plugin manager.
        
        This will unload any loaded plugin.
        
        """
        logger.info('Closing plugin manager...')
        # important not to use an iterator over self._plugins since it is
        # modified in the unload method
        for id in self._plugins.keys():
            self._unload_and_notify(id)
        logger.info('Plugin manager closed')
    
    def configure_service(self):
        """Return an object providing the IConfigureService interface.
        
        You can then configure certain aspect of the plugin manager via this
        object.
        
        """
        return self._cfg_service
    
    def _db_pathname(self):
        return os.path.join(self._plugins_dir, self._DB_FILENAME)

    def _join_server_url(self, p):
        server = self.server
        if server is None:
            logger.warning('Plugin manager server attribute is not set')
            raise InvalidParameterError("'server' has no value set")
        else:
            if server.endswith('/'):
                return server + p
            else:
                return server + '/' + p
    
    def _extract_plugin(self, cache_filename):
        with contextlib.closing(tarfile.open(cache_filename)) as tfile:
            # XXX this is unsafe unless we have authenticated the tarfile
            tfile.extractall(self._plugins_dir)
    
    def install(self, id):
        """Install a plugin.
        
        This does not check if the plugin is already installed and does not
        load the newly installed plugin.

        Return a tuple (deferred, operation in progress).
        
        Raise an Exception if there's already an install/upgrade operation
        in progress for the plugin.
        
        Raise an Exception if there's no installable plugin with the
        specified id.
        
        Raise an InvalidParameterError if the plugin package is not in cache
        and no 'server' param has been set.
        
        """
        logger.info('Installing plugin %s', id)
        if id in self._in_install:
            logger.warning('Install operation already in progress for plugin %s', id)
            raise Exception('an install/upgrade operation for plugin %s is already in progress' % id)
        
        try:
            pg_info = self._get_installable_plugin_info(id)
        except KeyError:
            logger.error('Can\'t install plugin %s: not found', id)
            raise
        filename = pg_info['filename']
        cache_filename = os.path.join(self._cache_dir, filename)
        if os.path.isfile(cache_filename):
            try:
                self._extract_plugin(cache_filename)
            except Exception, e:
                top_deferred = defer.fail(e)
                top_oip = OperationInProgress(self._INSTALL_LABEL, OIP_FAIL)
            else:
                top_deferred = defer.succeed(None)
                top_oip = OperationInProgress(self._INSTALL_LABEL, OIP_SUCCESS)
        else:
            url = self._join_server_url(filename)
            rfile = RemoteFile(cache_filename, url, self._downloader, pg_info['dsize'])
            sha1hook = SHA1Hook(a2b_hex(pg_info['sha1sum']))
            dl_deferred, dl_oip = async_download_with_oip(rfile, [sha1hook])
            dl_oip.label = self._DOWNLOAD_LABEL
            self._in_install.add(id)
            top_deferred = defer.Deferred()
            top_oip = OperationInProgress(self._INSTALL_LABEL, OIP_PROGRESS, sub_oips=[dl_oip])
            def dl_callback(_):
                self._in_install.remove(id)
                try:
                    self._extract_plugin(cache_filename)
                except Exception, e:
                    top_oip.state = OIP_FAIL
                    top_deferred.errback(e)
                else:
                    top_oip.state = OIP_SUCCESS
                    top_deferred.callback(None)
            def dl_errback(err):
                self._in_install.remove(id)
                top_oip.state = OIP_FAIL
                top_deferred.errback(err)
            # do not move this line up (see dl_callback def)
            dl_deferred.addCallbacks(dl_callback, dl_errback)
        def top_callback(res):
            logger.info('Plugin %s installed', id)
            return res
        def top_errback(err):
            logger.error('Error while installating plugin %s: %s', id, err.value)
            return err
        top_deferred.addCallbacks(top_callback, top_errback)
        return top_deferred, top_oip

    def upgrade(self, id):
        """Upgrade a plugin.
        
        Right now, there's is absolutely no difference between calling this
        method and calling the install method.
        
        """
        logger.info('Upgrading plugin %s', id)
        return self.install(id)
        
    def uninstall(self, id):
        """Uninstall a plugin.
        
        This does not unload the installed plugin.
        
        Raise an Exception if there's no installed plugin with the
        specified id.
        
        """
        logger.info('Uninstalling plugin %s', id)
        if not self.is_installed(id):
            logger.error('Can\'t uninstall plugin %s: not installed', id)
            raise Exception('plugin not found')
        
        shutil.rmtree(os.path.join(self._plugins_dir, id))

    def update(self):
        """Download a fresh copy of the plugin definition file from the server.
        
        Return a tuple (deferred, operation in progress)..
        
        Raise an Exception if there's already an update operation in progress.
        
        Raise an InvalidParameterError if no 'server' param has been set,
        or has an invalid value.
        
        Note:
        - if the downloaded plugin definition file is invalid/corrupted, no
          error will be raised in this method.
        - if the operation fail, for example because of an incomplete
          download, the local copy of the plugin definition file won't be
          changed
        
        """
        logger.info('Updating plugin definition file')
        if self._in_update:
            logger.warning('Update operation already in progress')
            raise Exception('an update operation is already in progress')

        url = self._join_server_url(self._DB_FILENAME)
        db_pathname = self._db_pathname()
        rfile = RemoteFile(db_pathname, url, self._downloader, None)
        dl_deferred, dl_oip = async_download_with_oip(rfile)
        dl_oip.label = self._UPDATE_LABEL
        self._in_update = True
        def callback(res):
            logger.info('Plugin definition file updated')
            return res
        def errback(err):
            logger.error('Error while updating plugin definition file: %s', err.value)
            return err
        def dl_end(v):
            self._in_update = False
            return v
        dl_deferred.addCallbacks(callback, errback)
        dl_deferred.addBoth(dl_end)
        return dl_deferred, dl_oip
    
    def _get_installable_plugin_info(self, id):
        # Return an 'installable plugin info' object from a id, or raise
        # a KeyError if no such plugin is found
        installable_plugins = self.list_installable()
        return installable_plugins[id]
    
    def list_installable(self):
        """Return a dictionary of installable plugins, where keys are
        plugin identifier and values are dictionary of plugin information.
        
        The plugin information dictionary contains the following keys:
          filename -- the name of the package in which the plugin is packaged
          version -- the version of the package
          description -- the description of the package
          dsize -- the download size of the package, in bytes
          sha1sum -- an hex representation of the sha1sum of the package
          capabilities -- a dictionary where keys are string in format
            "vendor, model, version" and values are capabilities dictionary.
        
        Raise an Exception if the plugin definition file is invalid/corrupted.
        If this file is absent, no error is raised, and an empty dictionary
        is returned.
        
        Note that the returned dictionary contains unicode strings instead
        of 'normal' string.
        
        """
        try:
            with open(self._db_pathname()) as fobj:
                raw_plugin_infos = json.load(fobj)
        except IOError:
            return {}
        else:
            for plugin_id, raw_plugin_info in raw_plugin_infos.iteritems():
                _check_raw_plugin_info(raw_plugin_info, plugin_id,
                                       _PLUGIN_INFO_INSTALLABLE_KEYS)
            return raw_plugin_infos
    
    def is_installed(self, id):
        """Return true if the plugin <id> is currently installed, else
        false.
        
        """
        return id in self.list_installed()
    
    def list_installed(self):
        """Return a dictionary of installed plugins, where keys are plugin
        identifier and value are dictionary of plugin information.
        
        See Plugin.info() method for more information on the returned
        dictionary.
        
        """
        # XXX can't iterate over loaded plugins (i.e. self._plugins) here
        #     because a plugin could be installed but not loaded (most common
        #     case is when loading the plugins at the start). We might want to
        #     rework a bit all this.
        installed_plugins = {}
        for rel_plugin_dir in os.listdir(self._plugins_dir):
            abs_plugin_dir = os.path.join(self._plugins_dir, rel_plugin_dir)
            if os.path.isdir(abs_plugin_dir):
                plugin_info_path = os.path.join(abs_plugin_dir, _PLUGIN_INFO_FILENAME)
                with open(plugin_info_path) as fobj:
                    raw_plugin_info = json.load(fobj)
                _check_raw_plugin_info(raw_plugin_info, rel_plugin_dir,
                                       _PLUGIN_INFO_INSTALLED_KEYS)
                installed_plugins[rel_plugin_dir] = raw_plugin_info
        return installed_plugins
    
    @staticmethod
    def _add_execfile(pg_globals, plugin_dir):
        # add 'execfile_' to pg_globals.
        def aux(filename, *args, **kwargs):
            if args:
                globals = args[0]
                args = args[1:]
            elif 'globals' in kwargs:
                globals = kwargs['globals']
                del kwargs['globals']
            else:
                globals = pg_globals
            # reinject execfile_ if not present
            if 'execfile_' not in globals:
                globals['execfile_'] = aux
            # if filename is relative, then it must be relative to the plugin dir
            if not os.path.isabs(filename):
                filename = os.path.join(plugin_dir, filename)
            execfile(filename, globals, *args, **kwargs)
        pg_globals['execfile_'] = aux
    
    def _execplugin(self, plugin_dir, pg_globals):
        entry_file = os.path.join(plugin_dir, self._ENTRY_FILENAME)
        self._add_execfile(pg_globals, plugin_dir)
        logger.debug('Executing plugin entry file "%s"', entry_file)
        execfile(entry_file, pg_globals)
    
    def attach(self, observer):
        """Attach an IPluginManagerObserver object to this plugin manager.
        
        Note that since observers are weakly referenced, you MUST keep a
        reference to each one somewhere in the application if you want them
        not to be immediatly garbage collected.
        
        """
        logger.debug('Attaching plugin manager observer %s', observer)
        if observer in self._observers:
            logger.info('Observer %s was already attached', observer)
        else:
            self._observers[observer] = None
    
    def detach(self, observer):
        """Detach an IPluginManagerObserver object to this plugin manager."""
        logger.debug('Detaching plugin manager observer %s', observer)
        try:
            del self._observers[observer]
        except KeyError:
            logger.info('Observer %s was not attached', observer)
    
    def _notify(self, id, action):
        # action is either 'load' or 'unload'
        logger.debug('Notifying observers: %s %s', action, id)
        for observer in self._observers.keys():
            try:
                logger.info('Notifying observer %s', observer)
                fun = getattr(observer, 'pg_' + action)
                fun(id)
            except Exception:
                logger.error('Error while notifying observer %s', observer, exc_info=True)
    
    def _load_and_notify(self, id, plugin):
        self._plugins[id] = plugin
        self._notify(id, 'load')
    
    def _unload_and_notify(self, id):
        # next line will raise a KeyError if the plugin is not loaded, which
        # is what we want and it must be done before notifying the observers
        plugin = self._plugins[id]
        self._notify(id, 'unload')
        logger.info('Closing plugin %s', id)
        try:
            plugin.close()
        except Exception:
            logger.error('Error while closing plugin %s', id, exc_info=True)
        finally:
            del self._plugins[id]
    
    @staticmethod
    def _is_plugin_class(obj):
        # return true if obj is a plugin class with IS_PLUGIN true
        return isinstance(obj, type) and issubclass(obj, Plugin) and \
               hasattr(obj, 'IS_PLUGIN') and getattr(obj, 'IS_PLUGIN')
    
    def load(self, id, gen_cfg={}, spec_cfg={}):
        """Load a plugin.
        
        Raise an Exception if the plugin is already loaded, since we offer
        a guarantee to plugin that no more then one instance is active at any
        time.
        
        Also raise an Exception if the plugin could not be loaded, either
        because there's no plugin with such a id or because of an error
        at plugin load time.
        
        gen_cfg -- a mapping object with general configuration parameters.
          These parameters are the same for every plugins.
        spec_cfg -- a mapping object with plugin-specific configuration
          parameters. These parameters are specific to every plugins.
        
        """
        logger.info('Loading plugin %s', id)
        if id in self._plugins:
            raise Exception('plugin %s is already loaded' % id)
        plugin_dir = os.path.join(self._plugins_dir, id)
        plugin_globals = {}
        self._execplugin(plugin_dir, plugin_globals)
        for obj in plugin_globals.itervalues():
            if self._is_plugin_class(obj):
                break
        else:
            raise Exception('plugin %s has no plugin class' % id)
        logger.debug('Creating plugin instance from class %s', obj)
        plugin = obj(self._app, plugin_dir, gen_cfg, spec_cfg)
        plugin.id = id
        self._load_and_notify(id, plugin)

    def unload(self, id):
        """Unload a plugin.
        
        Raise an Exception if the plugin is not loaded.
        
        """
        logger.info('Unloading plugin %s', id)
        self._unload_and_notify(id)
    
    # Dictionary-like methods for loaded plugin access
    
    def __contains__(self, key):
        return key in self._plugins
    
    def __iter__(self):
        return iter(self._plugins)
    
    def __getitem__(self, key):
        return self._plugins[key]
    
    def __len__(self):
        return len(self._plugins)
    
    def get(self, key, default=None):
        return self._plugins.get(key, default)
    
    def iterkeys(self): 
        return self._plugins.iterkeys()
    
    def iteritems(self):
        return self._plugins.iteritems()
    
    def itervalues(self):
        return self._plugins.itervalues()
    
    def keys(self):
        return self._plugins.keys()
    
    def items(self):
        return self._plugins.items()
    
    def values(self):
        return self._plugins.values()
