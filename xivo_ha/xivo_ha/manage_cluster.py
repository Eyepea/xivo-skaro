#!/usr/bin/env python

import subprocess
import os
from time import localtime, strftime

class ClusterResourceManager(object):
    def __init__(self, services = [], backup_directory = "/var/backups/pf-xivo/pf-xivo-ha",
                 global_options_file = "/etc/pf-xivo/xivo_ha/global_options"
                ):
        self.services            = services
        self.backup_directory    = backup_directory
        self.global_options_file = global_options_file

    def _filename(self, filename, directory):
        if not directory:
            directory = self.backup_directory
        if not filename:
            time       = strftime("%Y%m%d-%H%M%S", localtime())
            backup_file = "%s/pf-xivo-ha-%s.bck" % (directory, time)
        else:
            backup_file = "%s/%s" % (directory, filename)
        return backup_file

    def _cluster_command(self, args = []):
        '''
        command to manage cluster
        _cluster_command(['crm', 'command', 'arg']
        _cluster_command(['crm_verify', '-LV']
        return a turple with (stdout, return code)
        '''
        if args.__len__() is not 0:
            command = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
            ret     = command.wait()
            error   = command.stderr.__str__()
            result  = command.stdout.readlines()
            if error is not 'None':
                return (result, ret)
            else:
                raise OSError(error) 
        else:
            raise ValueError, "You have to provide command (args = %s)" % args

    def _cluster_backup(self, directory = '', filename = ''):
        '''
        cluster configuration backup
        '''
        backup_file = self._filename(filename, directory)
        args        = ['crm', 'configure', 'save', backup_file]
        return self._cluster_command(args)

    def _cluster_restore(self, directory = '', filename = ''):
        '''
        restore configuration
        '''
        backup_file = self._filename(filename, directory)
        if backup_file:
            if os.path.isfile(backup_file):
                args        = ['crm', 'configure', 'load', 'replace', backup_file]
                return self._cluster_command(args)
            else:
                raise IOError("the backup file does not exist")

    def _cluster_erase_configuration(self):
        '''
        erase all cluster data
        '''
        args = ['crm', 'configure', 'erase']
        self._cluster_command(args)

    def _cluster_rollback(self):
        # TODO
        pass
    def _cluster_check_status(self):
        '''
            return a turple with cluster status
        '''
        args = ['crm_verify', '-LV']
        return self._cluster_command(args)

    def _cluster_global_option(self):
        '''
        add cluster global action :
            disable stonith (for tests purpose)
            - crm configure property stonith-enabled=false
            disable quorum (not needed for two nodes cluster)
            - crm configure property no-quorum-policy=ignore
            all resource must be in the same node :
            - crm configure rsc_defaults resource-stickiness=100
        '''
        properties   = ["stonith-enabled=false", "no-quorum-policy=ignore"]
        rsc_defaults = ["resource-stickiness=100"]

        global_options_file = self.global_options_file 
        with open(global_options_file, 'w') as file_:
            file_.write("configure\n")
            for prop in properties:
                file_.write("\tproperty %s\n" % prop)
            for rcs in rsc_defaults:
                file_.write("\trsc_defaults %s\n" % rcs)
            file_.write("\tcommit\n")
        # push config
        args = ['crm', '-f', global_options_file]
        return self._cluster_command(args)

    def _resource_primitive(self, rsc,
                            rsc_class = '',
                            rsc_provider = '',
                            rsc_type = '',
                            rsc_params = '',
                            rsc_operation = '',
                            rsc_op = [],
                           ):
        '''
        configure resource
        '''
        # for lsb provider is /etc/init.d/ file
        if rsc_class == 'lsb' and not rsc_provider:
            rsc_provider = rsc

        if rsc_class:
            rsc_class    = " %s" % rsc_class
            
        if rsc_provider:
            rsc_provider = ":%s" % rsc_provider

        if rsc_type:
            rsc_type     = ":%s" % rsc_type

        if rsc_params:
            rsc_params   = " params %s" % rsc_params

        if rsc_operation:
            rsc_operation = " operation %s" % operation

        rsc_op_result = ''
        if rsc_op:
            for elem in rsc_op:
                rsc_op_result = rsc_op_result + " op %s" % elem 
            
            
        result = "primitive " + rsc + rsc_class + rsc_provider + rsc_type + rsc_params + rsc_operation + rsc_op_result
        return result


    def _resource_order(self):
        '''
        define start order
        return a turple with data
        '''
        pass
    
    def _resource_colocation(self):
        '''
        define if resource must be on the same node
        return a turple with data
        '''
        pass

    def _resource_group(self):
        '''
        create a group with resource
        return a turple with data
        '''
        pass
    
    def _resource_monitor(self):
        '''
        monitor resource
        return a turple with data
        '''
        pass

    def _resource_master_slave(self):
        '''
        used for mysql/pgsql
        '''
        pass
    
    def _cluster_configure_service(self):
        '''
        add service in cluster
        '''
        pass

    def initialize(self):
        # TODO use lsb information (insserv) to start services
        # in right order
        #self._cluster_backup()
        #if self._cluster_status():
        #    # pass globals options
        #    self._cluster_global_option()
        #    self._cluster_configure_service()
        #    return True
        #else:
        #    self._cluster_rollback()
        pass

    def update(self):
        raise NotImplementedError
    

class DatabaseManagement(object):
    '''
    Used to manage database
    '''
    def __init__(self):
        pass

    def initialize(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
