#!/usr/bin/env python
# -*- coding: utf8 -*-
__author__  = "Nicolas HICHER <nhicher@proformatique.com>"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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
import os
import re
import sys
import filecmp
import shutil
import subprocess
import hashlib
from time import localtime, strftime
from xivo_ha.tools import Tools

class ClusterEngine(Tools):
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
        # TODO use cluster command
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

class ManageService(Tools):
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
        args = ['insserv', '-r', self.service_name]
        result, ret, error = self._cluster_command(args)
        return result, ret, error
    
    def _stop_service(self):
        args = ['/etc/init.d/%s' % self.service_name, 'stop']
        result, ret, error = self._cluster_command(args)
        return result, ret, error


    def initialize(self):
        if self._is_available():
            sys.stdout.write("disable %s autostart\n" % self.service_name)
            try:
                self._disable_service()
            except:
                raise IOError("impossible to disable service %s" % self.service_name)

            """
            sys.stdout.write("stopping %s \n" % self.service_name)
            try:
                self._stop_service()
            except:
                raise IOError("impossible to stop service %s" % self.service_name)
            """
            return True
        else:
            return False

class FilesReplicationManagement(Tools):
    '''
    Used to manage files replication
    '''
    def __init__(self,data):
        self.hosts         = data['hosts']
        self.role          = data['role']
        self.itf           = data['data_itf'] if data.has_key('data_itf') else None
        self.extra_include = data['extra_include'] if data.has_key('extra_include') else None
        self.extra_exclude = data['extra_exclude'] if data.has_key('extra_exclude') else None
        self.config_tmp    = data['config_tmp']  if data.has_key('config_tmp')  else '/usr/share/pf-xivo-ha/templates/csync2/csync2.cfg' 
        self.key_file      = data['key_file']    if data.has_key('key_file')    else "/etc/csync2.key"
        self.config_file   = data['config_file'] if data.has_key('config_file') else "/etc/csync2.cfg"
        self.backup_dir    = data['backup_dir']  if data.has_key('backup_dir')  else '/var/backups/pf-xivo/xivo_ha/csync2' 
        self.backup_keep   = data['backup_keep'] if data.has_key('backup_keep') else '/var/backups/pf-xivo/xivo_ha/csync2' 
        self.conflict_res  = 'younger'

    def _generate_ssl_key(self, time = None):
        if time is None:
            time = strftime("%Y%m%d-%H%M%S", localtime())
        string = "%s%s%s" % (self.hosts[0], self.hosts[1], time )
        return hashlib.md5(string).hexdigest()

    def _create_key_file(self):
        key_file = self.key_file
        if not os.path.isfile(key_file):
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
            if self.itf:
                string += " %s@%s-%s" % (host, host, self.itf)
            else:
                string += " %s" % host
        string += ";"
        return string

    def _config_file_key(self):
        string = "key"
        string += " %s;" % self.key_file
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

    
    def _config_file_include(self, include):
        string = "include"
        string += " %s;" % include
        return string

    def _config_file_exclude(self, exclude):
        string = "exclude"
        string += " %s;" % exclude
        return string

    def _create_config_file(self):
        template = open(self.config_tmp).readlines()
        config_file = self.config_file
        with open(config_file, 'w') as file_:
            for line in template:
                line = line.rstrip()
                if line == '\tHOSTS;':
                    file_.write(self._format_string(self._config_file_hosts()))
                elif line == '\tKEY;':
                    file_.write(self._format_string(self._config_file_key()))
                elif line == '\tBACKUP_DIR;':
                    file_.write(self._format_string(self._config_file_backup_dir()))
                elif line == '\tBACKUP_KEEP;':
                    file_.write(self._format_string(self._config_file_backup_rotate()))
                elif line == '\tCONFLICT_RESOLUTION;':
                    file_.write(self._format_string(self._config_file_conflict_resolution()))
                elif line == '\tEXTRA_INCLUDE;':
                    if self.extra_include:
                        for include in self.extra_include:
                            file_.write(self._format_string(self._config_file_include(include)))
                elif line == '\tEXTRA_EXCLUDE;':
                    if self.extra_exclude:
                        for exclude in self.extra_exclude:
                            file_.write(self._format_string(self._config_file_exclude(exclude)))
                            
                else:
                    file_.write('%s\n' % line)
        return config_file


    def initialize(self):
        '''
        create /etc/csync2.cfg and /etc/csync2.key on master
        normalize files on slave
        '''
        role = self.role
        if role == 'master':
            key_file   = self._create_key_file()
            config_file = self._create_config_file()
            sys.stdout.write('you have to copy %s and %s on slave\n' % (config_file, key_file))
        sys.stdout.write('Done\n')


    def update(self):
        '''
        updating /etc/csync2.conf
        '''
        print('updating csync2')
