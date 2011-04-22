#!/usr/bin/env python

import subprocess
import os
import time
from time import localtime, strftime

class ClusterResourceManager(object):
    def __init__(self, services   = [],
                 cluster_name     = None,
                 cluster_addr     = None,
                 cluster_itf      = None,
                 cluster_group    = False, 
                 backup_directory = "/var/backups/pf-xivo/pf-xivo-ha",
                 cluster_cfg      = "/etc/pf-xivo/xivo_ha/cluster.cfg",
                ):
        self.services         = services
        self.cluster_name     = cluster_name
        self.cluster_addr     = cluster_addr
        self.cluster_itf      = cluster_itf
        self.cluster_group    = cluster_group
        self.backup_directory = backup_directory
        self.cluster_cfg      = cluster_cfg

    def _filename(self, filename, directory):
        if not directory:
            directory = self.backup_directory
        if not filename:
            time       = strftime("%Y%m%d-%H%M%S", localtime())
            backup_file = "%s/pf-xivo-ha-%s.bck" % (directory, time)
        else:
            backup_file = "%s/%s" % (directory, filename)
        return backup_file

    # Cluster Management
    def _cluster_command(self, args = []):
        '''
        command to manage cluster
        _cluster_command(['crm', 'command', 'arg']
        _cluster_command(['crm_verify', '-LV']
        return a turple with (stdout, return code)
        '''
        if args.__len__() is not 0:
            command = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
            error   = command.stderr.__str__()
            result  = command.stdout.readlines()
            ret     = command.wait()
            if ret is 0:
                return (result)
            if ret is 2:
                return ret
            else:
                raise OSError(result) 
        else:
            raise ValueError, "You have to provide command (args = %s)" % args

    def _cluster_backup(self, directory = '', filename = ''):
        '''
        cluster configuration backup
        '''
        backup_file = self._filename(filename, directory)
        args        = ['crm', 'configure', 'save', backup_file]
        if self._cluster_command(args) == []:
            return True

    def _cluster_restore(self, directory = '', filename = ''):
        '''
        restore configuration
        '''
        backup_file = self._filename(filename, directory)
        if backup_file:
            if os.path.isfile(backup_file):
                args        = ['crm', 'configure', 'load', 'replace', backup_file]
                if self._cluster_command(args) == []:
                    return True
            else:
                raise IOError("the backup file does not exist")

    def _cluster_erase_configuration(self):
        '''
        erase all cluster data
        '''
        args = ['crm', 'configure', 'erase']
        return self._cluster_command(args)

    def _cluster_rollback(self):
        # TODO
        pass

    def _cluster_check_status(self):
        '''
            return a turple with cluster status
        '''
        args = ['crm_verify', '-LV']
        return self._cluster_command(args)

    def _cluster_check_if_configurable(self):
        '''
        check if resource is run on the cluster
        '''
        args = ['crm', 'resource', 'show']
        data =  self._cluster_command(args)
        if data[0][0].strip() is not 'NO resources configured':
            return True

    def _cluster_push_config(self):
        '''
        add service in cluster
        '''
        if self._cluster_check_if_configurable():
            args = ['crm', '-f', self.cluster_cfg]
            data = self._cluster_command(args)
            if data == []:
                return True
            else:
                return data

    def _cluster_resource_state(self, res):
        '''
        return resource state (running, stopped)
        '''
        args = ['crm', 'resource', 'show', res]
        data = self._cluster_command(args)
        res_state = data[0].split()[3]
        lsb_args = ['/etc/init.d/%s', 'status']
        if res_state == 'NOT':
            res_state = 'stopped'
        return res_state
        

    def _cluster_get_all_resources(self):
        '''
        return list with all configured resources
        '''
        all_res = []
        args = ['crm', 'resource', 'show']
        data =  self._cluster_command(args)
        for elem in data:
            if elem.split()[0] != 'Resource':
                all_res.append(elem.split()[0])
        return all_res
    
    def _cluster_stop_resource(self, res):
        '''
        to stop a resource
        '''
        result = []
        if self._cluster_resource_state(res) == 'running':
            args = ['crm', 'resource', 'stop', res]
            result = self._cluster_command(args)
        return result


    def _cluster_stop_all_resources(self):
        '''
        to stop all resources
        '''
        data = self._cluster_get_all_resources()
        if data.__contains__('NO'):
            pass
        for res in data:
            if self._cluster_resource_state(res) == 'running':
                self._cluster_stop_resource(res)
        return True
    # Cluster configuration
    def _cluster_property(self, stonith = False, quorum_policy = 'ignore'):
        '''
        to manage cluster properties
        return list
        '''
        if not stonith:
            state = 'false'
        else:
            state = 'true'
        stonith = "property stonith-enabled=%s" % state
        quorum  = "property no-quorum-policy=%s" % quorum_policy
        return [stonith, quorum]

    def _cluster_rsc_defaults(self, *args):
        '''
        to manage cluster rsc_defaults
        return list
        '''
        result = []
        for a in args:
            result.append("rsc_defaults %s" % a)
        return result

    def _resource_primitive(self, rsc,
                            rsc_class = None,
                            rsc_provider = None,
                            rsc_type = None,
                            rsc_params = None,
                            rsc_operation = None,
                            rsc_op = [],
                           ):
        '''
        configure resource
        return string
        '''
        # for lsb provider is /etc/init.d/ file
        if rsc_class == 'lsb' and not rsc_provider:
            rsc_provider = rsc

        rsc_class     = '' if rsc_class is None else ' %s' % rsc_class
        rsc_provider  = '' if rsc_provider is None else ":%s" % rsc_provider
        rsc_type      = '' if rsc_type is None else ":%s" % rsc_type
        rsc_params    = '' if rsc_params is None else " params %s" % rsc_params
        rsc_operation = '' if rsc_operation is None else " operation %s" % rsc_operation

        rsc_op_result = ''
        if rsc_op:
            for elem in rsc_op:
                rsc_op_result = rsc_op_result + " op %s" % elem 
            
            
        result = "primitive " + rsc + rsc_class + rsc_provider + rsc_type + rsc_params + rsc_operation + rsc_op_result
        return result

    def _format_string(self, string):
        string = "\t" + string + "\n"
        return string

    def _cluster_configure(self):
        '''
        create cluster config file
        '''
        cluster_cfg = self.cluster_cfg
        if os.path.isfile(cluster_cfg):
            os.rename(cluster_cfg, cluster_cfg + ".bck")

        with open(cluster_cfg, 'w') as file_:
            file_.write("configure\n")

            for prop in self._cluster_property():
                file_.write(self._format_string(prop))

            for rsc_prop in self._cluster_rsc_defaults('resource-stickiness=100'):
                file_.write(self._format_string(rsc_prop))
            if self.cluster_addr:
                file_.write(self._format_string(self._cluster_addr()))
            for service in self.services:
                file_.write(self._format_string(self._resource_primitive(service, rsc_class = 'lsb')))
            if self.cluster_group:
                group = self._resource_group(self.services)
                file_.write(self._format_string(group))

            file_.write(self._format_string(self._resources_order()))
            file_.write(self._format_string(self._resources_colocation()))
            file_.write("\tcommit\n")
        return cluster_cfg

    def _services_order(self, services):
        # TODO
        return services

    def _resources_order(self):
        '''
        define start order
        return a string with data
        use lsb informations to find the right order
        '''
        name = self.cluster_name
        result = 'order order_%s inf:' % name
        # add cluster_addr first
        ip_res = self._cluster_addr()
        if ip_res:
            result += " ip_%s:start" % name

        if not self.cluster_group:
            # TODO: use lsb information to lauch data in the right order
            services = self._services_order(self.services)
            for service in services:
                result += " %s:start" % service
        else:
            result +=  " group_%s:start" % name
        return result
        
    def _resources_colocation(self):
        '''
        define if resource must be on the same node
        return a string with data
        '''
        name = self.cluster_name
        result = 'colocation colocation_%s inf:' % name
        # add cluster_addr first
        ip_res = self._cluster_addr()
        if ip_res:
            result += " ip_%s" % name
        if not self.cluster_group:
            for service in self.services:
                result += " %s" % service
        else:
            result +=  " group_%s" % name
        return result


    def _resource_group(self, resources,
                        group_name   = None,
                        group_meta   = None,
                        group_params = None
                       ):
        '''
        create a group with resource
        return a string with data
        mandatory:
        - group_name
        - resources (list)
        '''
        group_name = self.cluster_name if group_name is None else group_name
        group_res  = "group group_%s" % group_name
        for res in resources:
            group_res += " %s" % res

        group_meta   = '' if group_meta is None else ' meta %s' % group_meta
        group_params = '' if group_params is None else ' params %s' % group_params
        return group_res + group_meta + group_params
    
    def _resource_monitor(self, rsc,
                            monitor_role     = None,
                            monitor_interval = None,
                            monitor_timeout  = None
                         ):
        '''
        monitor resource
        mandatory :
         - rsc
         - interval (in millisecond)
        optional :
         - timeout in s
         - role (only used with master/slave)
        return a string 
        '''
        monitor_role     = '' if monitor_role is None else ':%s' % monitor_role
        monitor_interval = '' if monitor_interval is None else ' %sm' % monitor_interval
        monitor_timeout  = '' if monitor_timeout is None else ':%ss' % monitor_timeout
        return 'monitor ' + rsc + monitor_role + monitor_interval + monitor_timeout

    def _resource_master_slave(self):
        '''
        used for mysql/pgsql
        '''
        raise NotImplementedError

    def _cluster_addr(self, cluster_addr_name = None):
        if cluster_addr_name is None:
            cluster_addr_name = "ip_%s" % self.cluster_name
        if self.cluster_addr and self.cluster_itf:
            ip_params = 'ip="%s" nic="%s"' % (self.cluster_addr, self.cluster_itf)
            return self._resource_primitive(cluster_addr_name,
                                             rsc_class    = "ocf",
                                             rsc_provider = 'heartbeat',
                                             rsc_type     = "IPaddr2",
                                             rsc_params   = ip_params
                                            )
    

    def cluster_manager(self):
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
