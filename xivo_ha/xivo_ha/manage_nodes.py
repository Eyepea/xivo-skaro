#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
import filecmp
import shutil

class ClusterEngine(object):
    def __init__(self, network_addr, multicast_addr, 
                    templates_path = '/usr/share/pf-xivo-ha/templates/corosync',
                    config_file    = "/etc/corosync/corosync.conf",
                    default_file   = "/etc/default/corosync"
            ):
        self.network_addr   = network_addr
        self.multicast_addr = multicast_addr
        self.templates_path = templates_path
        self.config_file    = config_file
        self.default_file   = default_file

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

            ip_addr_pattern = "\t\tbindnetaddr: IP_ADDR\n"
            mc_addr_pattern = "\t\tmcastaddr: MCAST_ADDR\n"

            ip_addr_string  = "\t\tbindnetaddr: %s\n" % self.network_addr
            mc_addr_string  = "\t\tmcastaddr: %s\n" % self.multicast_addr

            for l in data.readlines():
                if l == ip_addr_pattern:
                    l = ip_addr_string
                elif l == mc_addr_pattern:
                    l = mc_addr_string
                f.write(l)
            f.close()
            return (temp_file, self.config_file)
        except:
            raise

    def _deploy_config_file(self, new_file, old_file):
        '''
        deploy new config file
        '''
        if not filecmp.cmp(new_file, old_file, shallow = False):
            os.rename(new_file, old_file)
            return True
        else:
            os.delete(new_file)
            return False

    def _corosync_running(self):
        '''
        check if service is running
        '''
        if not os.path.isfile("/var/run/corosync.pid"):
            return False
        return True

    def _manage_corosync(self, action):
        # TODO use subprocess
        '''
        corosync service management : 
            start|stop|restart|force-reload|status
        '''
        try:
            os.system("invoke-rc.d corosync %s" % action)
            return True
        except:
            return False

    def initialize(self):
        '''
        create config files, lauch service
        '''
        if not self._corosync_running():
            # create config file
            try:
                self._enabled_corosync()
                temp_file, config_file = self._create_corosync_config_file()
                self._deploy_config_file(temp_file, config_file)
            except:
                raise
            # TODO: find a method to test service
            # start service
            try:
                self._manage_corosync("start")
            except:
                raise("Impossible to start corosync")

    def update(self):
        pass

class ManageServices(object):
    def __init__(self):
        pass
    def _disable_service():
        # TODO use subprocess
        pass
