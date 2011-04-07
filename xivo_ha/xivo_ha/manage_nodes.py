#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
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
        return False

    def _create_corosync_config_file(self):
        '''
        create corosync config file
        '''
        try:
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
        except:
            raise

    def _deploy_config_file(self, new_file, old_file):
        '''
        deploy new config file
        '''
        if not filecmp.cmp(new_file, old_file):
            os.rename(new_file, old_file)
            return True
        else:
            os.delete(new_file)
            return False

    def _corosync_not_running(self):
        '''
        check if service is running
        '''
        if not self._manage_corosync("status", 3):
            if self._manage_corosync("stop"):
                return True
        else:
            return True


    def _manage_corosync(self, action, ret = 0):
        '''
        corosync service management : 
            start|stop|restart|force-reload|status
        '''
        try:
            args = [self.init_file, action]
            state = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            if state.wait() == ret:
                return True
            else:
                raise state.stderr.readline()
        except:
            raise IOError("impossible to start corosync") 

    def initialize(self):
        '''
        create config files, lauch service
        '''
        if self._corosync_not_running():
            # create config file
            try:
                if not self._enabled_corosync():
                    raise IOError("pb to enabling corosync")

                temp_file, config_file = self._create_corosync_config_file()

                if not self._deploy_config_file(temp_file, config_file):
                    raise IOError("impossible to create corosync.conf")
            except:
                raise IOError("impossible to configure corosync")
            # start service
            try:
                if self._manage_corosync("start"):
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
            file ="%s/%s" % (self.init_path, self.init_name)
        else:
            file ="%s/%s" % (self.init_path, self.service_name)

        if os.path.isfile(file):
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
        if _is_available():
            _disable_service()
            return True
        else:
            return False


