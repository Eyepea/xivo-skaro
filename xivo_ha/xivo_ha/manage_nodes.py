#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
import sys
import filecmp
import shutil
import subprocess
import hashlib
from xivo_ha.tools import Tools

class ClusterEngine(object):
    def __init__(self, network_addr, multicast_addr, 
                    templates_path = '/usr/share/pf-xivo-ha/templates/corosync',
                    config_file    = "/etc/corosync/corosync.conf",
                    default_file   = "/etc/default/corosync",
                    init_file      = "/etc/init.d/corosync",
            ):
        self.network_addr   = network_addr
        self.multicast_addr = multicast_addr
        self.templates_path = templates_path
        self.config_file    = config_file
        self.default_file   = default_file
        self.init_file      = init_file

    def _check_if_configured(self, config_file, pattern):
        '''
        parse a file to find if pattern is present
        '''
        data =  open(config_file, 'r')
        for l in data.readlines():
            if re.match(pattern, l):
                return True
        return False

    def _enabled_corosync(self):
        '''
        enable corosync at boot time
        '''
        template = "%s/default_corosync" % self.templates_path
        self._template_available(template)

        if not self._check_if_configured(self.default_file, "START=yes"):
            shutil.copy2(template, self.default_file)
            return True

    def _template_available(self, template):
            if os.path.isfile(template):
                return os.path.isfile(template)
            else:
                raise IOError('template not accessible', template)

    def _create_corosync_config_file(self):
        '''
        create corosync config file
        '''
        temp_file = "%s.tmp" % self.config_file
        template = "%s/corosync.conf" % self.templates_path
        self._template_available(template)
        data = open(template, 'r')
        f = open(temp_file, 'w')

        ip_addr_pattern = ['bindnetaddr', 'IP_ADDR']
        mc_addr_pattern = ['mcastaddr', 'MCAST_ADDR']

        ip_addr_string  = "\t\tbindnetaddr: %s\n" % self.network_addr
        mc_addr_string  = "\t\tmcastaddr: %s\n" % self.multicast_addr

        for l in data.readlines():
            temp = [e.strip() for e in l.split(':')]
            if len(temp) == 2 and temp[0] == ip_addr_pattern[0] and temp[1] == ip_addr_pattern[1]:
                l = ip_addr_string
            if len(temp) == 2 and temp[0] == mc_addr_pattern[0] and temp[1] == mc_addr_pattern[1]:
                l = mc_addr_string
            f.write(l)
        f.close()

        if os.path.isfile(temp_file):
            return (temp_file, self.config_file)
        else:
            return False

    def _deploy_config_file(self, new_file, old_file):
        '''
        deploy new config file
        '''
        if not filecmp.cmp(new_file, old_file):
            os.rename(new_file, old_file)
            return True
        else:
            os.remove(new_file)
            return True

    def _corosync_not_running(self):
        '''
        stop corosync if it's running
        '''
        if not self._manage_corosync("status", 3):
            sys.stdout.write("stopping corosync\n")
            self._manage_corosync("stop")
        return True

    def _manage_corosync(self, action, ret = 0):
        '''
        corosync service management : 
            start|stop|restart|force-reload|status
        '''
        args = [self.init_file, action]
        state = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if state.wait() == ret:
            return True
        else:
            return False

    def initialize(self):
        '''
        create config files, lauch service
        '''
        if self._corosync_not_running():
            try:
                self._enabled_corosync()
            except:
                raise IOError("impossible to enable corosync in %s"
                               % self.default_file)
            try:
                temp_file, config_file = self._create_corosync_config_file()
                self._deploy_config_file(temp_file, config_file)
            except:
                raise IOError("impossible to write new corosync config file %s"
                               % self.config_file)
            # start service
            try:
                if self._manage_corosync("start"):
                    sys.stdout.write("starting corosync\n")
                    return True
            except:
                raise IOError("Impossible to start corosync")
            sys.stdout.write('Cluster Engine is configured and running\n')

    def update(self):
        pass

class ManageService(object):
    def __init__(self, service_name, init_path = "/etc/init.d", init_name = ''):
        self.service_name = service_name
        self.init_path = init_path
        self.init_name = init_name

    def _is_available(self):
        '''
        check if and init file exist for service
        '''
        if self.init_name:
            init_file ="%s/%s" % (self.init_path, self.init_name)
        else:
            init_file ="%s/%s" % (self.init_path, self.service_name)

        if os.path.isfile(init_file):
            return True
        else:
            return False

    def _disable_service(self):
        try:
            args = ['insserv', '-r', self.service_name]
            state = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            if state.wait() is 0:
                return True
            else:
                return state.stderr.readline()
        except:
            raise IOError("impossible to disable service %s" % self.service_name)

    def initialize(self):
        if self._is_available():
            self._disable_service()
            sys.stdout.write("disable %s autostart\n" % self.service_name)
            return True
        else:
            return False

class FilesReplicationManagement(Tools):
    '''
    Used to manage files replication
    '''
    def __init__(self,data):
        self.dirs         = data['dirs']
        self.files        = data['files']
        self.conflict_res = data['conflict_resolution']
        self.hosts        = data['hosts']
        self.key_file     = data['key_file']
        self.config_file  = data['config_file'] if data.has_key('config_file') else "/etc/csync.cfg"
        self.backup_dir   = data['backup_dir']
        self.backup_keep  = data['backup_keep']

    def _generate_ssl_key(self):
        string = "%s%s" % (self.hosts[0], self.hosts[1])
        return hashlib.md5(string).hexdigest()

    def _create_key_file(self):
        key_file = self.key_file
        key = self._generate_ssl_key()
        with open(key_file, 'w') as file_:
            file_.write(key)
        return key_file

    def _config_file_hosts(self):
        '''
        return a string with host statement
        '''
        string = "host"
        for host in self.hosts:
            string += " %s" % host
        string += ";"
        return string

    def _config_file_key_file(self):
        string = "key"
        string += " %s;" % self.key_file
        return string

    def _config_file_include(self, include):
        string = "include"
        string += " %s;" % include
        return string
    
    def _config_file_exclude(self, exclude):
        string = "exclude"
        string += " %s;" % exclude
        return string
   
    def _config_file_backup_dir(self):
        string = "backup-directory"
        string += " %s;" % self.backup_dir
        return string

    def _config_file_backup_rotate(self):
        string = "backup-generations"
        string += " %s;" % self.backup_keep
        return string

    def _config_file_conflict_resolution(self):
        string = "auto"
        string += " %s;" % self.conflict_res
        return string

    def _create_config_file(self):
        config_file = self.config_file
        with open(config_file, 'w') as file_:
            file_.write('group xivo\n')
            file_.write('{\n')
            # host statement
            file_.write(self._format_string(self._config_file_hosts()))
            # key file
            file_.write(self._format_string(self._config_file_key_file()))
            # manage include
            data = self.dirs + self.files
            for f in data:
                file_.write(self._format_string(self._config_file_include(f)))
            # backup dir
            file_.write(self._format_string(self._config_file_backup_dir()))
            # backup rotation
            file_.write(self._format_string(self._config_file_backup_rotate()))
            # key file
            file_.write(self._format_string(self._config_file_conflict_resolution()))
            file_.write('}\n')

        return config_file

    def initialize(self):
        sys.stdout.write("create configuration file for csync2")
        self._create_config_file()

    def start(self):
        raise NotImplementedError
