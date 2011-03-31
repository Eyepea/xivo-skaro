#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import re
import filecmp
import shutil

class ClusterEngine(object):
    def __init__(self, network_addr, multicast_addr, 
            templates_path = '/usr/share/pf-xivo-ha/templates/corosync'):
        self.network_addr   = network_addr
        self.multicast_addr = multicast_addr
        self.templates_path = templates_path

    def _check_if_configured(self, config_file, pattern):
        '''
        parse a file to find if pattern is present
        '''
        data =  open(config_file, 'r')
        for l in data.readlines():
            if re.match(pattern, l):
                return True
        return False

    def _enabled_corosync(self, default_file = "/etc/default/corosync"):
        '''
        enable corosync at boot time
        '''
        template = "%s/default_corosync" % self.templates_path
        if not self._check_if_configured(default_file, "START=yes"):
            shutil.copy2(template, default_file)

    def _create_corosync_config_file(self, config_file = "/etc/corosync/corosync.conf"):
        '''
        create corosync config file
        '''
        temp_file = "%s.tmp" % config_file
        template = "%s/corosync.conf" % self.templates_path
        data = open(template, 'r')
        f = open(temp_file, 'w')
        for l in data.readlines():
            if re.search("bindnetaddr:", l):
                if not re.match(self.network_addr, l):
                    l = "\t\tbindnetaddr: %s\n" % self.network_addr
            elif re.search("mcastaddr:", l):
                if not re.match(self.multicast_addr, l):
                    l = "\t\tmcastaddr: %s\n" % self.multicast_addr
            f.write(l)
        f.close()
        self._deploy_config_file(temp_file, config_file)

    def _deploy_config_file(self, new_file, old_file):
        '''
        deploy new config file
        '''
        if not filecmp.cmp(new_file, old_file):
            os.rename(new_file, old_file)
        else:
            os.delete(new_file)

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
                self._create_corosync_config_file()
            except:
                raise("Impossible to create config file")
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
