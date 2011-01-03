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
import shutil
import tarfile
import weakref
from prov2 import progressop
from prov2.servers.tftp.service import TFTPFileService
from prov2.services import AttrConfigureServiceParam, BaseConfigureService,\
    IInstallService
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.web.static import File
from jinja2.environment import Environment
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from fetchfw2.download import new_handlers, new_downloaders
from fetchfw2.package import PackageManager, DefaultInstaller
from fetchfw2.storage import RemoteFileBuilder, InstallationMgrBuilder,\
    DefaultPackageStorage
from zope.interface import Attribute, Interface, implements


# TODO take proxy into account for downloading
# TODO support plugin package signing... this will be important for safety
#      since plugin aren't sandboxed

# 'Non-instantaneous' operation interface
# XXX name is not really good... and in fact, since it's close to a deferred,
#     we might want this to be a class deriving from Deferred and adding the
#     'status' attribute (hoping it will never get used in the future) so that
#     we could use the already existing deferred infrastructure
class IProgressingOperation(Interface):
    
    deferred = Attribute("""A Deferred that will fire once the operation is
                completed. Will either fire its callback with None if the
                operation completed successfully, or will fire its errback
                if the operated failed.""")
                
    status = Attribute("""A read-only string showing the status of the
                operation. Can have one of these values:
                
                success -- if the operation completed successfully
                fail -- if the operation failed
                progress -- if the operation is in progress
                progress;X/Y -- extended progress notation, where X and Y
                  are integer and where 0 <= X and 0 <= Y and X < Y (usually).
                
                """)


# XXX turn this into an Interface and make the distinction between what
#     should be accessible as attributes and what should be accesible as
#     methods
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
    name -- the name of the plugin. This attribute is set after the plugin
            instantiation time by the plugin manager
    _pluging_dir -- the base directory in which the plugin is
    _gen_cfg -- a read-only general configuration mapping object
    _spec_cfg -- a read-only plugin-specific configuration mapping object
    services
    http_dev_info_extractor
    http_service
    tftp_dev_info_extractor
    tftp_service
    device_types
    
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
    name = None
    
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
        spec_cfg --  a dictionary with plugin-specific configuration key-values
        
        """
        self._app = app
        self._plugin_dir = plugin_dir
        self._gen_cfg = gen_cfg
        self._spec_cfg = spec_cfg
    
    def close(self):
        """Close the plugin.
        
        This method is the last method called in the plugin unloading process.
        
        In normal situation, this method is guaranteed to be the last one
        called in the life-cycle of a plugin instance, and may not be called
        more than once.
        
        """
        pass
    
    # Methods for additional plugin services
    
    services = {}
    """Return a dictionary where keys are 'service name' and values are
    'service object'.
    
    This is used so that plugins can offer additional services in a
    standard way.
    
    If the 'service name' is one of the standardized service name, then
    the corresponding 'service object' must provide the 'standardized
    service interface' associated with this name.
    
    If the 'service name' is not one of the standardized service name,
    then it must provide the IUnknownService interface.
    
    """
    
    # Methods for TFTP/HTTP services
    
    # Contrary to TFTP and HTTP, there's no DHCP service, but only an extractor
    dhcp_dev_info_extractor = None
    """Return an object providing the IDeviceInfoExtrace interface for
    DHCP request or None if there's no such object.
    
    Request objects are dictionaries. There's one interesting key, 'dhcp_opts',
    which value is a dictionary which keys are integer representing the DHCP
    code option and value the raw DHCP value found in the client request.
    
    """
    
    # XXX now that device info extraction has been unified, with the type of
    #     the request being passed as an argument, we could have only one
    #     'dev_info_extractor' for each plugin. The plugin could then use the
    #     different 'generic' device info extractor (splitter and composite)
    http_dev_info_extractor = None
    """Return an object providing the IDeviceInfoExtractor interface for
    HTTP requests or None if there's no such object.
    
    In this case, request objects are twisted.web.http.Request objects.
    
    """
    
    http_service = None
    """The HTTP service of this plugin, or None if the plugin doesn't offer
    an HTTP service.
    
    In the case the plugins has no HTTP service, HTTP requests for the
    plugin will be served by the default HTTP service (normally done in
    a HTTPRequestProcessing object).
    
    XXX the request object passed to the render method of this service
    has a 'prov2_dev' attribute set to the device object which is doing
    this request, or None (but the attribute is always present).
    
    """
    
    tftp_dev_info_extractor = None
    """Return an object providing the IDeviceInfoExtractor interface for
    TFTP request or None if there's no such object.
    
    In this case, request objects are as defined in the
    prov2.servers.tftp.service module.
    
    """

    tftp_service = None
    """The TFTP service of this plugin, or None if the plugin
    doesn't offer a TFTP service.
    
    In the case the plugins has no TFTP service, TFTP requests for the
    plugin will be served by the default TFTP service (normally done in
    a TFTPRequestProcessing object).
    
    XXX the request object passed to the handle_read_request method of this
    service has a 'prov2_dev' key set to the device object which is doing
    this request, or None (but the attribute is always present).
    
    """
    
    device_types = ()
    """Return a sequence of (vendor, model, version) tuple that this plugin explicitly
    supports.
    
    Useful if we want to do automatic device-plugin association.
    XXX in fact, will be mostly useful to list to the user which models
    are supported by the plugin; this is not enough powerful to do
    interesting automatic device-plugin association
    
    """
    
    # Methods for device configuration
    
    # XXX scheduled for deletion -- lets see if its possible to do without
    #     this, and I guess it is, but it might be impratical, but let's
    #     implement only once we'll see that we're boned
    def configure_common(self, config):
        """Apply a non-device specific configuration to the plugin. In typical
        case, this will configure the 'common file' shared by all the devices.
        
        config is a mapping object with all the configurations parameters.
        Plugin class can modify this object.
        
        This method is synchronous/blocking.
        
        """ 
        pass
    
    def configure(self, dev, config):
        """Configure the plugin so that the config config is applied to the
        device dev. This method MUST not synchronize the configuration between
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
        
        Pre:  dev is a device object (can't be None)
              config is a 'flat' config object (can't be None). The plugin
                is free to modify this object (it won't affect anything).
                The meaning of the value in the config object are defined in
                the config module. Note that there's no guarantee that any of
                the value will be present. Also, to keep the phone in sync with
                the config, if a supported key is not present in the config,
                the plugin should configure the phone so that this key as its
                default or null value.
        Post: after a call to this method, if device dev does a request for
                its configuration file, its configuration will be as the
                config object
        
        This method is synchronous/blocking.
        
        XXX exception ? return value ?
        
        """
        pass
    
    def deconfigure(self, dev):
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
        
        Pre:  dev is a device object
              the method 'configure' has been called at least once with the
                same device object since the last call to deconfigure with
                the same devie (i.e. a method to deconfigure can only follow
                a call to the configure method with the same device, and there
                must not be a call to deconfigure between these 2 calls)
        Post: after a call to this method, if device dev does a request for
                its configuration file, it won't be configured with an old
                config (it's ok if the device is configured with the common
                configuration though)
        
        This method is synchronous/blocking.
        
        XXX exception ? return value ?
        
        """
        pass
    
    def synchronize(self, dev, config):
        """Force the device to synchronize its configuration so that its the
        same as the one in the config object.
        
        Note that to be succesful, the device must be online...
        
        Pre:  dev is a device object (can't be None)
              config is a config object (can't be None)
              there has been no change to the config object since the last
                call to the configure method with the same device object and
                config object. Said differently, before this call, there has
                been a call to configure with the same object, and there has
                been no call to deconfigure with the same dev object between
                these calls and no other call to configure with the same dev
                object.
        Post: if the device was online, its config has been reloaded
        
        Raise an Exception if the plugin doesn't know how to synchronize the
        device.
        
        Return a Deferred object that fire its callback with a None value if
        the reload seems to have been succesful, else fire its errback with an
        exception.
        
        XXX should we really use the errback or use the callback with a value
        meaningfull of the reason why the device did not reload ?
         
        """
        raise Exception("No known way to reload the device")


class StandardPlugin(Plugin):
    """Plugin that helps with having a standardized plugin layout and
    which helps with repeating tasks, etc etc, this is a bad description.
    
    """
    TFTPBOOT_DIR = os.path.join('var', 'tftpboot')
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        Plugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        self._tftpboot_dir = os.path.join(plugin_dir, self.TFTPBOOT_DIR)
        self.tftp_service = TFTPFileService(self._tftpboot_dir)
        # TODO this permits directory listing, which might or might not
        #      be desirable
        self.http_service = File(self._tftpboot_dir)  
    

class TemplatePluginHelper(object):
    DEFAULT_TPL_DIR = 'templates'
    """Directory where the default templates lies."""
    CUSTOM_TPL_DIR = os.path.join('var', 'templates')
    """Directory where the custom templates lies."""
    
    def __init__(self, plugin_dir):
        custom_dir = os.path.join(plugin_dir, self.CUSTOM_TPL_DIR)
        default_dir = os.path.join(plugin_dir, self.DEFAULT_TPL_DIR)
        loader = FileSystemLoader([custom_dir, default_dir])
        self._env = Environment(trim_blocks=True, loader=loader)
        
    def get_dev_template(self, filename, dev):
        """Get the device template used for the device specific configuration
        file.
        
        """
        # get device-specific template
        try:
            return self._env.get_template(filename + '.tpl')
        except TemplateNotFound:
            pass
        # get model-specific template
        if 'model' in dev:
            model = dev['model']
            try:
                return self._env.get_template(model + '.tpl')
            except TemplateNotFound:
                pass
        # get base template
        return self._env.get_template('base.tpl')
    
    def get_template(self, name):
        return self._env.get_template(name)
    
    def dump(self, template, context, filename, encoding='UTF-8', errors='strict'):
        tmp_filename = filename + '.tmp'
        template.stream(context).dump(tmp_filename, encoding, errors)
        os.rename(tmp_filename, filename)
    
    def render(self, template, context, encoding='UTF-8', errors='strict'):
        return template.render(context).encode(encoding, errors)

        
class _AsyncPackageManager(PackageManager):
    """Custom async package manager. The interface is a bit different from
    the standard PackageManager, but it's ok since it's to be used only
    internally.
    
    """
    
    def install(self, pkg_id):
        """Return a POP."""
        from twisted.internet import reactor
        async_installer = _AsyncInstaller(reactor)
        reactor.callInThread(async_installer, [pkg_id], self._installable_pkgs, self._installed_pkgs)
        return async_installer
    
    def upgrade(self, *args, **kwargs):
        raise NotImplementedError('async version not implemented because not needed')


class _AsyncInstaller(DefaultInstaller):
    implements(IProgressingOperation)
    
    def __init__(self, reactor, **kwargs):
        DefaultInstaller.__init__(self, **kwargs)
        self._reactor = reactor
        self.deferred = Deferred()
        self.status = 'progress'
        
    def __call__(self, pkg_names, installable_pkgs, installed_pkgs):
        """Note: SHOULD be called in a separate thread since its blocking."""
        try:
            # 1. Process package names
            clean_pkg_names = self._clean_pkg_names(pkg_names, installable_pkgs, installed_pkgs)
            to_install_pkgs = self._get_pkgs_to_install(clean_pkg_names, installable_pkgs, installed_pkgs)
            # 2. Download the files
            self._pre_download(to_install_pkgs)
            # TODO override download so that the status is updated
            self._download(to_install_pkgs)
        except Exception, e:
            self.status = 'fail'
            self._reactor.callFromThread(self.deferred.errback, e)
            raise
        else:
            def second_step():
                # this part is made to be executed in the reactor thread
                try:
                    # 3. Install packages
                    self._pre_install(to_install_pkgs)
                    new_pkgs = self._install(to_install_pkgs)
                    self._post_install(new_pkgs)
                    # 4. step normally done in package manager -- update installed_pkgs
                    for new_pkg in new_pkgs:
                        installed_pkgs[new_pkg.name] = new_pkg
                    installed_pkgs.flush()
                    # 5. fire callback
                    self.status = 'success'
                    self.deferred.callback(None)
                except Exception, e:
                    self.status = 'fail'
                    self.deferred.errback(e)
            self._reactor.callFromThread(second_step)


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
    def new_rfile_builder(cls, http_proxy=None, ftp_proxy=None):
        handlers = new_handlers(http_proxy, ftp_proxy)
        dlers = new_downloaders(handlers)
        return RemoteFileBuilder(dlers)
    
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
        if pkg_id in self._in_install_set:
            raise Exception("an install operation for pkg '%s' is already in progress" % pkg_id)
        if pkg_id not in self._async_pkg_manager.installable_pkgs:
            raise Exception('package not found')

        # FIXME right now, it's possible to have 2 download for the same
        #       file at the same time, which would lead to some bad things
        #       We could mitigate this by using a remote file object that
        #       download to an arbitrarly name file before renaming, so we
        #       could have 2 download of the same file at the same time with
        #       I believe no consequence
        pop = self._async_pkg_manager.install(pkg_id)
        self._in_install_set.add(pkg_id)
        def on_success_or_error(_):
            self._in_install_set.remove(pkg_id)
        pop.deferred.addBoth(on_success_or_error)
        return pop
    
    def uninstall(self, pkg_id):
        """Uninstall a package.
        
        See IInstallService.uninstall.
        
        """
        self._async_pkg_manager.uninstall((pkg_id,))

    def list_installable(self):
        """Return a list of the packages that are isntallable.
        
        See IInstallService.list_installable.
        
        """
        installable_pkgs = self._async_pkg_manager.installable_pkgs
        res = []
        for pkg in installable_pkgs.itervalues():
            dsize = sum(rfile.size for rfile in pkg.remote_files)
            res.append({'id': pkg.name, 'dsize': dsize})
        return res
        
    def list_installed(self):
        """Return a list of the packages that are installed.
        
        See IInstallService.list_installed.
        
        """
        installed_pkgs = self._async_pkg_manager.installed_pkgs
        installed_pkgs.reload()
        return [{'id': pkg.name} for pkg in installed_pkgs.itervalues()]
    
    def services(self):
        """Return the following dictionary: {'install': self}."""
        return {'install': self}


class StaticProgressingOperation(object):
    def __init__(self, deferred, status):
        self.deferred = deferred
        self.status = status

def pop_succeed(result):
    return StaticProgressingOperation(defer.succeed(result), 'success')

def pop_fail(result=None):
    return StaticProgressingOperation(defer.fail(result), 'fail')

class _InstallProxyProgressingOperation(object):
    implements(IProgressingOperation)
    
    def __init__(self, pop):
        self._pop = pop
        self.deferred = defer.Deferred()
        self._status = 'progress'
    
    @property
    def status(self):
        if self._pop.status not in ('success', 'fail'):
            return self._pop.status
        return self._status


class IPluginManagerObserver(object):
    """Interface that objects which want to be notified of plugin
    loading/unloading MUST provide.
    
    """
    def pg_load(pg_id):
        pass
    
    def pg_unload(pg_id):
        pass


class BasePluginManagerObserver(object):
    def __init__(self, pg_load=None, pg_unload=None):
        self._pg_load = pg_load
        self._pg_unload = pg_unload
    
    def pg_load(self, pg_id):
        if self._pg_load is not None:
            self._pg_load(pg_id)
    
    def pg_unload(self, pg_id):
        if self._pg_unload is not None:
            self._pg_unload(pg_id)


# XXX we could use 'id' instead of 'name' since we are using 'id' at the other
#     places
class PluginManager(object):
    """Manage the life cycle of plugins in the plugin ecosystem.
    
    PgMgr objects have a 'server' attribute which represent the base address
    of the plugins repository (ex.: http://www.example.com/prov2/stable). It
    can be set to None if no server is specified.
    
    A 'plugin info' object is a mapping object with the following keys:
      name -- the plugin name
      version -- the plugin version (not to mistake with the version 
                of the device the plugin supports)
    
    An 'installable plugin info' is a 'plugin info' object + the following keys:
      filename -- the name of the file to download on the remote server (i.e.
                  the name of the plugin package)
    
    """
    
    # TODO proxy awareness... a shame that twisted web client proxy support
    #      is vague, and when we'll do this, we'll probably want to take
    #      the 'general configure service' to look up the proxy value
    
    _ENTRY_FILENAME = 'entry.py'
    """The name of the python plugin code."""
    _DEF_FILENAME = 'defs'
    """The plugin definition filename on the remote and local server."""
    _INFO_FILENAME = 'plugin-info'
    """The name of the plugin information file."""
    
    def __init__(self, app, plugins_dir, cache_dir):
        """
        app -- an application object
        plugins_dir -- the directory where plugins are installed
        cache_dir -- a directory where plugin-package are downloaded, or None
          if no cache is to be used
        
        """
        self._app = app
        self._plugins_dir = plugins_dir
        self._cache_dir = cache_dir
        # XXX move the cfg_service stuff out of the PgMgr ?
        server_p = AttrConfigureServiceParam(self, 'server',
                                             'The base address of the plugins repository')
        self._cfg_service = BaseConfigureService({'server': server_p})
        self._in_update = False
        self._in_install_set = set()
        self._observers = weakref.WeakKeyDictionary()
        self._plugins = {}
        self.server = None
    
    def close(self):
        """Close the plugin manager.
        
        This will unload any loaded plugin.
        
        """
        for name in self._plugins:
            self._unload_and_notify(name)
    
    def configure_service(self):
        """Return an object providing the IConfigureService interface.
        
        You can then configure certain aspect of the plugin manager via this
        object.
        
        """
        return self._cfg_service
    
    def _def_pathname(self):
        return os.path.join(self._plugins_dir, self._DEF_FILENAME)

    def _join_server_url(self, p):
        server = self._server
        if server is None:
            raise ValueError("'server' has no value set")
        else:
            if server.endswith('/'):
                return server + p
            else:
                return server + '/' + p
    
    def _is_in_cache(self, filename):
        """Return the pathname of the cached plugin package if it exists,
        else return None.
        
        """
        cache_filename = os.path.join(self._cache_dir, filename)
        if os.path.isfile(cache_filename):
            return True
        return False
    
    def _download_plugin(self, filename, cache_filename):
        """Return an object providiing IProgressOperation that will fire
        when the download is ready."""
        # filename is the part that needs to be concatened to the server
        # URL, cache_filename is the (final) destination of the download
        # XXX share quite some similtude with update()
        url = self._join_server_url(filename)
        tmp_filename = cache_filename + '.tmp'
        fdst = open(tmp_filename, 'wb')
        try:
            pop = progressop.request(url, fdst)
        except Exception:
            raise ValueError("invalid 'server' value")
            fdst.close()
            os.remove(tmp_filename)
        else:
            def on_error(failure):
                fdst.close()
                os.remove(tmp_filename)
                return failure
            def on_success(_):
                fdst.close()
                os.rename(tmp_filename, cache_filename)
            pop.deferred.addCallbacks(on_success, on_error)
            return pop
    
    def _extract_plugin(self, cache_filename):
        with contextlib.closing(tarfile.open(cache_filename)) as tfile:
            # XXX this is unsafe unless we have authenticated the tarfile
            tfile.extractall(self._plugins_dir)
    
    def install(self, name):
        """Install a plugin.
        
        This does not check if the plugin is already installed and does not
        load the newly installed plugin.

        Return an object providing the IProgressOperation interface.
        
        Raise an Exception if there's already an install/upgrade operation
        in progress for the plugin.
        
        Raise an Exception if there's no installable plugin with the specified
        name.
        
        Raise an InvalidParameterError if the plugin package is not in cache
        and no 'server' param has been set.
        
        """
        if name in self._in_install_set:
            raise Exception("an install/upgrade operation for plugin '%s' is already in progress" % name)
        
        pg_info = self._get_installable_pg_info(name)
        if pg_info is None:
            raise ValueError('plugin not found')
        
        cache_filename = os.path.join(self._cache_dir, pg_info['filename'])
        if not self._is_in_cache(cache_filename):
            self._in_install_set.add(name)
            dl_pop = self._download_plugin(pg_info['filename'], cache_filename)
            proxy_pop = _InstallProxyProgressingOperation(dl_pop)
            def on_error(failure):
                self._in_install_set.remove(name)
                proxy_pop._status = 'fail'
                proxy_pop.deferred.errback(failure)
            def on_success(_):
                self._in_install_set.remove(name)
                try:
                    self._extract_plugin(cache_filename)
                except Exception, e:
                    proxy_pop._status = 'fail'
                    proxy_pop.deferred.errback(e)
                else:
                    proxy_pop._status = 'success'
                    proxy_pop.deferred.callback(None)
            dl_pop.deferred.addCallbacks(on_success, on_error)
            return proxy_pop
        else:
            try:
                self._extract_plugin(cache_filename)
            except Exception, e:
                return pop_fail(e)
            else:
                return pop_succeed(None)

    def upgrade(self, name):
        """Upgrade a plugin.
        
        Right now, there's is absolutely no difference between calling this
        method and calling the install method.
        
        """
        return self.install(name)
        
    def uninstall(self, name):
        """Uninstall a plugin.
        
        This does not unload the installed plugin.
        
        """
        pg_info = self._get_installed_pg_info(name)
        if pg_info is None:
            raise ValueError('plugin not found')
        
        shutil.rmtree(os.path.join(self._plugins_dir, name))

    def update(self):
        """Download a fresh copy of the plugin definition file from the server.
        
        Return an object providing the IProgressingOperation interface.
        
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
        if self._in_update:
            raise Exception("an update operation is already in progress")

        url = self._join_server_url(self._DEF_FILENAME)
        def_pathname = self._def_pathname()
        tmp_pathname = def_pathname + '.tmp'
        fdst = open(tmp_pathname, 'wb')
        try:
            pop = progressop.request(url, fdst)
        except Exception:
            raise ValueError("invalid 'server' value")
            fdst.close()
            os.remove(tmp_pathname)
        else:
            self._in_update = True
            def on_error(failure):
                self._in_update = False
                fdst.close()
                os.remove(tmp_pathname)
                return failure
            def on_success(_):
                self._in_update = False
                fdst.close()
                os.rename(tmp_pathname, def_pathname)
            pop.deferred.addCallbacks(on_success, on_error)
            return pop
    
    def _get_installable_pg_info(self, name):
        """Return an 'installable plugin info' object from a name, or None if
        no such plugin is found."""
        for pg_info in self.list_installable():
            if pg_info['name'] == name:
                return pg_info
        return None
    
    def list_installable(self):
        """Return a generator that yield information on the plugins that can
        be installed.
        
        Each yieled object is a dictionary with the following keys:
          name -- the name of the plugin
          version -- the verison of the plugin
          filename -- the name of the package in which the plugin is packaged
        
        The generator will eventually raise an Exception if the plugin definition
        file is invalid/corrupted. If this file is absent, no error is raised,
        but the generator will yield no items (i.e. like an 'empty' plugin
        definition file).
        
        """
        config = ConfigParser.RawConfigParser()
        try:
            with open(self._def_pathname(), 'r') as fobj:
                config.readfp(fobj)
        except IOError:
            pass
        else:
            for section in config.sections():
                if not section.startswith('plugin_'):
                    raise ValueError('invalid plugin definition file')
                name = section[len('plugin_'):]
                filename = config.get(section, 'filename')
                version = config.get(section, 'version')
                yield {'name': name, 'filename': filename, 'version': version}
    
    def _get_installed_pg_info(self, name):
        """Return an 'installed plugin info' object from a name, or None if
        no such plugin is found."""
        for pg_info in self.list_installed():
            if pg_info['name'] == name:
                return pg_info
        return None
    
    def is_installed(self, name):
        """Return true if the plugin <name> is currently installed, else
        false.
        
        """
        return self._get_installed_pg_info(name) != None
    
    def list_installed(self):
        """Return a generator that yield information on the plugins that are
        installed.
        
        Each yielded object is a dictionary with the following keys:
          name -- the name of the plugin
          version -- the verison of the plugin
        
        The generator will eventually raise an Exception if, in the plugins
        directory, there's a directory which has a missing or invalid plugin
        info file.
        
        """
        for rel_plugin_dir in os.listdir(self._plugins_dir):
            abs_plugin_dir = os.path.join(self._plugins_dir, rel_plugin_dir)
            if os.path.isdir(abs_plugin_dir):
                info_pathname = os.path.join(abs_plugin_dir, self._INFO_FILENAME)
                with open(info_pathname, 'r') as fobj:
                    config = ConfigParser.ConfigParser()
                    config.readfp(fobj)
                version = config.get('general', 'version')
                yield {'name': rel_plugin_dir, 'version': version}
    
    def list_upgradeable(self):
        """Return a generator that yield information the plugins that can be
        upgraded.
        
        Each yielded object is a dictionary with the following keys:
          name -- the name of the plugin
          version -- the version of the plugin
          filename -- the name of the package in which the plugin is packaged
        
        This method will raise an Exception in the same circumstances as the
        generator returned by the list_installed method.
        
        The generator will raise an Exception in the same circumstances as the
        list_installable method.
        
        """    
        installed = dict((plugin['name'], plugin['version']) for plugin in
                         self.list_installed())
        # XXX the version comparison is cheap
        upgradable = (plugin for plugin in self.list_installable() if
                      plugin['name'] in installed and
                      plugin['version'] > installed.get(plugin['name'], ''))
        return upgradable
    
    @staticmethod
    def _add_execfile(pg_globals, plugin_dir):
        """Add 'execfile_' to pg_globals."""
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
        execfile(entry_file, pg_globals)
    
    def attach(self, observer):
        """Attach an IPluginManagerObserver object to this plugin manager.
        
        Note that since observers are weakly referenced, you MUST keep a
        reference to each one somewhere in the application if you want them
        not to be immediatly garbage collected.
        
        """
        if observer not in self._observers:
            self._observers[observer] = None
    
    def detach(self, observer):
        """Detach an IPluginManagerObserver object to this plugin manager."""
        try:
            del self._observers[observer]
        except KeyError:
            pass
    
    def _notify(self, pg_id, action):
        # action is either 'load' or 'unload'
        for ob in self._observers.keys():
            fun = getattr(ob, 'pg_' + action)
            fun(pg_id)
    
    def _load_and_notify(self, name, plugin):
        self._plugins[name] = plugin
        self._notify(name, 'load')
    
    def _unload_and_notify(self, name):
        plugin = self._plugins[name]
        plugin.close()
        del self._plugins[name]
        self._notify(name, 'unload')
    
    def load(self, name, gen_cfg={}, spec_cfg={}):
        """Load a plugin.
        
        Raise an Exception if the plugin is already loaded, since we offer
        a guarantee to plugin that no more then one instance is active at any
        time.
        
        Also raise an Exception if the plugin could not be loaded, either
        because there's no plugin with such a name or because of an error
        at plugin load time.
        
        gen_cfg -- a mapping object with general configuration parameters.
          These parameters are the same for every plugins.
        spec_cfg -- a mapping object with plugin-specific configuration
          parameters. These parameters are specific to every plugins.
        
        """
        if name in self._plugins:
            raise Exception("plugin '%s' is already loaded" % name)
        plugin_dir = os.path.join(self._plugins_dir, name)
        plugin_globals = {}
        self._execplugin(plugin_dir, plugin_globals)
        for el in plugin_globals.itervalues():
            if (isinstance(el, type) and 
                issubclass(el, Plugin) and
                hasattr(el, 'IS_PLUGIN') and
                getattr(el, 'IS_PLUGIN')):
                    plugin = el(self._app, plugin_dir, gen_cfg, spec_cfg)
                    plugin.name = name
                    self._load_and_notify(name, plugin)
                    return
        else:
            raise Exception("pg '%s': no plugin class found in file" % name)

    def unload(self, name):
        """Unload a plugin.
        
        Raise an Exception if the plugin is not loaded.
        
        """
        self._unload_and_notify(name)

    def load_all(self, gen_cfg={}, spec_cfg_map={}):
        """Load all the installed plugins.
        
        Already loaded plugin WILL NOT be reloaded.
        
        spec_cfg_map -- a mapping object where keys are plugin name and
          values are plugin-specific configuration parameters. 
        
        """
        # spec_cfg_map is a mapping which keys are plugin name and which values are
        # specific configuration mapping for the plugin with this name
        for pg_info in self.list_installed():
            pg_name = pg_info['name']
            if pg_name not in self._plugins:
                self.load(pg_name, gen_cfg, spec_cfg_map.get(pg_name, {}))
    
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
