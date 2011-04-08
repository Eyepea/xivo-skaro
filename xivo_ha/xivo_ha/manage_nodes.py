#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
import sys
import filecmp
import shutil
import subprocess

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
        if not self._check_if_configured(self.default_file, "START=yes"):
            shutil.copy2(template, self.default_file)
            return True

    def _create_corosync_config_file(self):
        '''
        create corosync config file
        '''
        temp_file = "%s.tmp" % self.config_file
        template = "%s/corosync.conf" % self.templates_path
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
            sys.stdout.write("stopping corosync, please be patient\n")
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


