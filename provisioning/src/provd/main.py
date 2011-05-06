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

# XXX the names are confusing, sometimes they refer to stuff here sometimes
#     they refer to similarly named stuff in ident.py. The name process_service
#     is certainly the most confusing of them. We should really try to fix this

import logging.handlers
import os.path
import provd.config
import provd.devices.ident
import provd.devices.pgasso
from provd.app import ProvisioningApplication
from provd.devices.config import ConfigCollection
from provd.devices.device import DeviceCollection
from provd.servers.tftp.proto import TFTPProtocol
from provd.servers.http_site import Site
from provd.persist.memory import MemoryDatabaseFactory
from provd.persist.shelve import ShelveDatabaseFactory
from provd.rest.server.server import new_server_resource,\
    new_restricted_server_resource
from twisted.application.service import IServiceMaker, Service, MultiService
from twisted.application import internet
from twisted.internet import ssl
from twisted.plugin import IPlugin
from twisted.python import log
from twisted.web.resource import Resource
from zope.interface.declarations import implements

logger = logging.getLogger(__name__)


class ProvisioningService(Service):
    # has an 'app' attribute after starting
    
    _DB_FACTORIES = {
        'list': MemoryDatabaseFactory(),
        'dict': MemoryDatabaseFactory(),
        'shelve': ShelveDatabaseFactory()
    }
    
    def __init__(self, config):
        self._config = config

    def _extract_database_specific_config(self):
        db_config = {}
        for k, v in self._config.iteritems():
            pre, sep, post = k.partition('.')
            if pre == 'database' and sep and post not in ['type', 'generator']:
                db_config[post] = v
        return db_config
    
    def _create_database(self):
        db_type = self._config['database.type']
        db_generator = self._config['database.generator']
        db_specific_config = self._extract_database_specific_config()
        logger.info('Using %s database with %s generator and config %s',
                    db_type, db_generator, db_specific_config)
        db_factory = self._DB_FACTORIES[db_type]
        return db_factory.new_database(db_type, db_generator, **db_specific_config)
    
    def _close_database(self):
        logger.info('Closing database...')
        try:
            self._database.close()
        except Exception:
            logger.error('Error while closing database', exc_info=True)
        logger.info('Database closed')
    
    def startService(self):
        self._database = self._create_database()
        try:
            cfg_collection = ConfigCollection(self._database.collection('configs'))
            dev_collection = DeviceCollection(self._database.collection('devices'))
            if self._config['database.ensure_common_indexes']:
                logger.debug('Ensuring index existence on collections')
                try:
                    dev_collection.ensure_index(u'mac')
                    dev_collection.ensure_index(u'ip')
                    dev_collection.ensure_index(u'sn')
                except AttributeError, e:
                    logger.warning('This type of database doesn\'t seem to support index: %s', e)
            self.app = ProvisioningApplication(cfg_collection, dev_collection, self._config)
        except Exception:
            try:
                raise
            finally:
                self._close_database()
        else:
            Service.startService(self)
    
    def stopService(self):
        Service.stopService(self)
        try:
            self.app.close()
        except Exception:
            logger.error('Error while closing application', exc_info=True)
        self._close_database()


class ProcessService(Service):
    def __init__(self, prov_service, config):
        self._prov_service = prov_service
        self._config = config
    
    def _get_conffile_globals(self):
        # Pre: hasattr(self._prov_service, 'app')
        conffile_globals = {}
        conffile_globals.update(provd.devices.ident.__dict__)
        conffile_globals.update(provd.devices.pgasso.__dict__)
        conffile_globals['app'] = self._prov_service.app
        return conffile_globals
    
    def _create_processor(self, request_config_dir, name, config_name):
        # name is the name of the processor, for example 'info_extractor'
        filename = os.path.join(request_config_dir, name + '.py.conf.' + config_name)
        conffile_globals = self._get_conffile_globals()
        try:
            execfile(filename, conffile_globals)
        except Exception, e:
            logger.error('error while executing process config file "%s": %s', filename, e)
            raise
        if name not in conffile_globals:
            raise Exception('process config file "%s" doesn\'t define a "%s" name',
                            filename, name)
        return conffile_globals[name]
    
    def startService(self):
        # Pre: hasattr(self._prov_service, 'app')
        self.request_processing = provd.devices.ident.RequestProcessingService(self._prov_service.app)
        request_config_dir = self._config['general.request_config_dir']
        for name in ['info_extractor', 'retriever', 'updater', 'router']:
            setattr(self.request_processing, 'dev_' + name,
                    self._create_processor(request_config_dir, name, self._config['general.' + name]))
        Service.startService(self)


class HTTPProcessService(Service):
    def __init__(self, prov_service, process_service, config):
        self._prov_service = prov_service
        self._process_service = process_service
        self._config = config
    
    def startService(self):
        app = self._prov_service.app
        process_service = self._process_service.request_processing
        http_process_service = provd.devices.ident.HTTPRequestProcessingService(process_service,
                                                                                app.pg_mgr) 
        site = Site(http_process_service)
        port = self._config['general.http_port']
        interface = self._config['general.ip']
        if interface == '*':
            interface = ''
        logger.info('Binding HTTP provisioning service to "%s:%s"', interface, port)
        self._tcp_server = internet.TCPServer(port, site, interface=interface)
        self._tcp_server.startService()
        Service.startService(self)

    def stopService(self):
        Service.stopService(self)
        return self._tcp_server.stopService()


class TFTPProcessService(Service):
    def __init__(self, prov_service, process_service, config):
        self._prov_service = prov_service
        self._process_service = process_service
        self._config = config
    
    def startService(self):
        app = self._prov_service.app
        process_service = self._process_service.request_processing
        tftp_process_service = provd.devices.ident.TFTPRequestProcessingService(process_service,
                                                                                app.pg_mgr)
        tftp_protocol = TFTPProtocol(tftp_process_service)
        port = self._config['general.tftp_port']
        interface = self._config['general.ip']
        if interface == '*':
            interface = ''
        logger.info('Binding TFTP provisioning service to "%s:%s"', interface, port)
        self._udp_server = internet.UDPServer(port, tftp_protocol, interface=interface)
        self._udp_server.startService()
        Service.startService(self)
    
    def stopService(self):
        Service.stopService(self)
        return self._udp_server.stopService()


class DHCPProcessService(Service):
    # has a 'dhcp_request_processing_service' attribute once started
    def __init__(self, process_service):
        self._process_service = process_service
    
    def startService(self):
        process_service = self._process_service.request_processing
        self.dhcp_request_processing_service = provd.devices.ident.DHCPRequestProcessingService(process_service)
        Service.startService(self)


class RemoteConfigurationService(Service):
    def __init__(self, prov_service, dhcp_process_service, config):
        self._prov_service = prov_service
        self._dhcp_process_service = dhcp_process_service
        self._config = config
    
    def startService(self):
        app = self._prov_service.app
        dhcp_request_processing_service = self._dhcp_process_service.dhcp_request_processing_service
        if self._config['general.rest_is_public']:
            server_resource = new_server_resource(app, dhcp_request_processing_service)
            logger.warning('No authentication is required for REST API')
        else:
            credentials = (self._config['general.rest_username'],
                           self._config['general.rest_password'])
            server_resource = new_restricted_server_resource(app, dhcp_request_processing_service, credentials)
            logger.info('Authentication is required for REST API')
        root_resource = Resource()
        root_resource.putChild('provd', server_resource)
        rest_site = Site(root_resource)
        
        port = self._config['general.rest_port']
        interface = self._config['general.rest_ip']
        if interface == '*':
            interface = ''
        logger.info('Binding HTTP REST API service to "%s:%s"', interface, port)
        if self._config['general.rest_ssl']:
            logger.info('SSL enabled for REST API')
            context_factory = ssl.DefaultOpenSSLContextFactory(self._config['general.rest_ssl_keyfile'],
                                                               self._config['general.rest_ssl_certfile'])
            self._tcp_server = internet.SSLServer(port, rest_site, context_factory, interface=interface)
        else:
            self._tcp_server = internet.TCPServer(port, rest_site, interface=interface)
        self._tcp_server.startService()
        Service.startService(self)
    
    def stopService(self):
        Service.stopService(self)
        return self._tcp_server.stopService()


class _CompositeConfigSource(object):
    def __init__(self, options):
        self._options = options
        
    def pull(self):
        raw_config = {}
        
        default = provd.config.DefaultConfigSource()
        raw_config.update(default.pull())
        
        command_line = provd.config.CommandLineConfigSource(self._options)
        raw_config.update(command_line.pull())
        
        config_file = provd.config.ConfigFileConfigSource(raw_config['general.config_file'])
        raw_config.update(config_file.pull())
        
        return raw_config


class ProvisioningServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    
    tapname = 'provd'
    description = 'A provisioning server.'
    options = provd.config.Options
    
    def _configure_logging(self, options):
        # configure standard logging module
        if options['stderr']:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        else:
            handler = logging.handlers.SysLogHandler('/dev/log', logging.handlers.SysLogHandler.LOG_DAEMON)
            handler.setFormatter(logging.Formatter('provd[%(process)d]: %(message)s'))
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        if options['verbose']:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.INFO)
        # configure twisted.log module
        observer = log.PythonLoggingObserver()
        observer.start()
        # XXX next line doesn't work, it seems impossible to completely
        # disable twisted log observers when starting an app with twistd
        # without resorting to ugly hacks
        #log.startLoggingWithObserver(observer.emit, False)
    
    def _read_config(self, options):
        logger.info('Reading application configuration')
        config_sources = [_CompositeConfigSource(options)]
        return provd.config.get_config(config_sources)
    
    def makeService(self, options):
        self._configure_logging(options)
        
        config = self._read_config(options)
        top_service = MultiService()
        
        # check config for verbosity
        if config['general.verbose']:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Day oh')
        
        prov_service = ProvisioningService(config)
        prov_service.setServiceParent(top_service)
        
        process_service = ProcessService(prov_service, config)
        process_service.setServiceParent(top_service)
        
        http_process_service = HTTPProcessService(prov_service, process_service, config)
        http_process_service.setServiceParent(top_service)
        
        tftp_process_service = TFTPProcessService(prov_service, process_service, config)
        tftp_process_service.setServiceParent(top_service)
        
        dhcp_process_service = DHCPProcessService(process_service)
        dhcp_process_service.setServiceParent(top_service)
        
        remote_config_service = RemoteConfigurationService(prov_service, dhcp_process_service, config)
        remote_config_service.setServiceParent(top_service)

        return top_service
