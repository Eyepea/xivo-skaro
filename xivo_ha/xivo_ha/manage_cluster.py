#!/usr/bin/env python
# -*- coding: utf8 -*-
__author__  = "Nicolas HICHER <nhicher@proformatique.com>, Guillaume Bour <gbour@proformatique.com>"
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
import subprocess
import os
import sys
import time
import hashlib
import re
from xivo_ha.tools import Tools
from time import localtime, strftime

PG_ETC = '/etc/postgresql/9.0/main'
PG_VAR = '/var/lib/postgresql'

class ClusterResourceManager(Tools):
    def __init__(self,
                 cluster_config   = {},
                 backup_directory = "/var/backups/pf-xivo/xivo_ha",
                 cluster_cfg      = "/etc/pf-xivo/xivo_ha/cluster.cfg",
                 pf_scripts       = "/usr/share/pf-xivo-ha/bin",
                ):
        if cluster_config != {}:
            self.services         = cluster_config['services'].keys()
            self.services_data    = cluster_config['services']
            #self.extra_scripts    = cluster_config['scripts'] if cluster_config.has_key('scripts') else None
            self.cluster_nodes    = cluster_config['cluster_nodes']
            self.cluster_name     = cluster_config['cluster_name']
            self.cluster_monitor  = cluster_config['cluster_monitor']
            self.cluster_timeout  = cluster_config['cluster_timeout']
            self.cluster_mailto   = cluster_config['cluster_mailto'] if cluster_config.has_key('cluster_mailto') else None
            self.cluster_pingd    = cluster_config['cluster_pingd'] if cluster_config.has_key('cluster_pingd') else None
            self.cluster_addr     = cluster_config['cluster_addr'] if cluster_config.has_key('cluster_addr') else None
            self.cluster_group    = cluster_config['cluster_group'] if cluster_config.has_key('cluster_group') else None
            self.backup_directory = backup_directory
            self.cluster_cfg      = cluster_cfg
            self.pf_scripts       = pf_scripts

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
    def _cluster_backup(self, directory = '', filename = ''):
        '''
        cluster configuration backup
        '''
        backup_file = self._filename(filename, directory)
        args        = ['crm', 'configure', 'save', backup_file]
        result, ret, err = self._cluster_command(args)
        if ret is not 0:
            raise IOError(result)
        else:
            return True

    def _cluster_restore(self, directory = '', filename = ''):
        '''
        restore configuration
        '''
        backup_file = self._filename(filename, directory)
        if backup_file:
            if os.path.isfile(backup_file):
                args        = ['crm', 'configure', 'load', 'replace', backup_file]
                result, ret, error = self._cluster_command(args)
                if ret is 0:
                    return True
                else:
                    return result
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
            data, ret, error = self._cluster_command(args)
            if data == []:
                return 'ok'
            else:
                return data

    def _cluster_resource_state(self, res):
        '''
        return resource state (running, stopped)
        '''
        if res != 'NO':
            args = ['crm', 'resource', 'show', res]
            data, res, error = self._cluster_command(args)
            res_state = data[0].split()[3]
            if res_state == 'NOT':
                res_state = 'stopped'
            return res_state
        else:
            return 'stopped'
        
    def _cluster_resource_show(self):
        '''
        get cluster resources state
        '''
        args = ['crm', 'resource', 'show']
        data, res, error =  self._cluster_command(args)
        return data, res, error

    def _cluster_configure_show(self, res = None):
        '''
        get cluster configuration 
        '''
        args = ['crm', 'configure', 'show']
        if res:
            args.append(res)
        data, res, error =  self._cluster_command(args)
        return data, res, error

    def _cluster_get_group_members(self):
        '''
        return a dict with all groups and members
        '''
        data, res, error = self._cluster_configure_show()
        group_members = {}
        groups = []
        for elem in data:
            if re.search('^group.*', elem):
                groups.append(elem.split()[1])
        for group in groups:
            full_string = []
            data, res, error = self._cluster_configure_show(group)
            for elem in data:
                elem = elem.strip().split()
                if '\\' in elem:
                    elem.remove('\\')
                full_string += elem
                # remove non used data
                if 'group' in full_string:
                    full_string.remove('group')
                if 'meta' in full_string:
                    index = full_string.index('meta')
                    srv = full_string[1:index]
                    group_members[full_string[0]] = sorted(srv)
                else:
                    group_members[full_string[0]] = sorted(full_string[1:])
        return group_members

    def _cluster_get_all_resources(self):
        '''
        return list with all configured resources
        '''
        resources = []
        data, res, error =  self._cluster_configure_show()
        for elem in data:
            if re.search('^primitive.*', elem):
                elem = elem.split()
                resources.append(elem[1])
        return resources
    
    def _cluster_stop_resource(self, resource):
        '''
        to stop a resource
        '''
        result = []
        res    = None
        error  = None
        if self._cluster_resource_state(resource) == 'running':
            args = ['crm', 'resource', 'stop', resource]
            result, res, error = self._cluster_command(args)
        return result, res, error


    def _cluster_stop_all_resources(self):
        '''
        to stop all resources
        '''
        resources = self._cluster_get_all_resources()
        # pass if there is no resource
        if resources.__contains__('NO'):
            pass
        # if resource is in group, stop group, not resource
        if self.cluster_pingd:
            self._cluster_stop_resource('pingdclone')
        if self.cluster_group:
            groups = self._cluster_get_group_members()
            groups_members = []
            for group, members in groups.iteritems():
                for member in members:
                    if member in resources:
                        resources.remove(member)
                self._cluster_stop_resource(group)
        
        if resources:
            for resource in resources:
                self._cluster_stop_resource(resource)
        time.sleep(4)
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
        if self.services_data.has_key(rsc):
            rsc_class = self.services_data[rsc]['rsc_class']
            # for lsb provider is /etc/init.d/ file
            if rsc_class == 'lsb' and rsc_provider is None:
                rsc_provider = rsc

            # by default heartbeat is with ocf
            if rsc_class == 'ocf' and rsc_provider is None:
                rsc_provider = 'heartbeat'
                if rsc_type is None:
                    rsc_type = rsc

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

    def _resource_pf_scripts(self):
        name = "scripts_%s" % self.cluster_name
        primitive = 'primitive %s ocf:heartbeat:pf-xivo-ha-scripts' % name
        return name, primitive

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
               for itf in self._cluster_addr().iteritems():
                   file_.write(self._format_string(itf[1]))

            # we need to create a group_srv_member with services and scripts to avoid
            # monitoring and timeout on scripts
            group_srv_members = []
            for service in self.services:
                file_.write(self._format_string(self._resource_primitive(service, rsc_class = 'lsb')))
                group_srv_members.append(service)

            # add scripts
            if os.listdir(self.pf_scripts) != '':
                scripts_name, scripts_primitive = self._resource_pf_scripts()
                file_.write(self._format_string(scripts_primitive))
                group_srv_members.append(scripts_name)

            # configure mail
            if self.cluster_mailto:
                mailto_name, mailto_primitive = self._cluster_mailto()
                file_.write(self._format_string(mailto_primitive))
                group_srv_members.append(mailto_name)

            if self.cluster_pingd:
                pingd_primitive, pingd_clone = self._cluster_pingd()
                file_.write(self._format_string(pingd_primitive))
                file_.write(self._format_string(pingd_clone))
                
            if self.cluster_group:
                group_name = 'srv_%s' % self.cluster_name
                group = self._resource_group(group_srv_members, group_name = group_name)
                file_.write(self._format_string(group))
            if len(self.cluster_addr) > 1:
                ip_group_name = 'ip_%s' % self.cluster_name
                ip_group = self._resource_group(self._cluster_addr().keys(), group_name = ip_group_name)
                file_.write(self._format_string(ip_group))


            for res, val in self.services_data.iteritems():
                monitor_interval = val['monitor'] if val.has_key('monitor') else self.cluster_monitor
                monitor_timeout  = val['timeout'] if val.has_key('timeout') else self.cluster_timeout
                monitor_role     = val['role']    if val.has_key('role')    else None
                file_.write(self._format_string(self._resource_monitor(res, monitor_interval, monitor_timeout, monitor_role)))

            file_.write(self._format_string(self._resources_location()))
            file_.write(self._format_string(self._resources_order()))
            file_.write(self._format_string(self._resources_colocation()))
            file_.write("\tcommit\n")

        return cluster_cfg

    def _services_order(self, services):
        # TODO
        return services.sort()

    def _resources_location(self, prefered_node = None, score = None):
        '''
        to manage cluster location
        '''
        name = self.cluster_name
        prefered_node = self.cluster_nodes[0] if prefered_node is None else prefered_node 
        score = '100' if score is None else score 
        result = 'location location_%s' % name 
        ip_res = self._cluster_addr()
        if ip_res > 1:
            result += " group_ip_%s" % name
        else:
            result += " ip_%s" % name
        result += " %s:" % score
        result += " %s" % prefered_node
        return result


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
        if ip_res > 1:
            result += " group_ip_%s:start" % name
        else:
            result += " ip_%s:start" % name

        if not self.cluster_group:
            # TODO: use lsb information to lauch data in the right order
            # services = self._services_order(self.services)
            # at the moment, it is just sorted
            for service in sorted(self.services):
                result += " %s:start" % service
        else:
            result +=  " group_srv_%s:start" % name
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
        if ip_res > 1:
            result += " group_ip_%s" % name
        else:
            result += " ip_%s" % name
        if not self.cluster_group:
            # same as _resources_order
            # need refactoring
            for service in sorted(self.services):
                result += " %s" % service
        else:
            result +=  " group_srv_%s" % name
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
                            monitor_interval = None,
                            monitor_timeout  = None,
                            monitor_role     = None
                         ):
        '''
        monitor resource
        mandatory :
         - rsc
        optional :
         - timeout in s
         - interval 
         - role (only used with master/slave)
        return a string 
        '''
        monitor_role     = '' if monitor_role is None else ':%s' % monitor_role
        monitor_interval = self.cluster_monitor if monitor_interval is None else monitor_interval
        monitor_timeout  = self.cluster_timeout if monitor_timeout is None else monitor_timeout
        interval = ' %s' % monitor_interval
        timeout  = ':%s' % monitor_timeout
        return 'monitor ' + rsc + monitor_role + interval + timeout

    def _resource_master_slave(self):
        '''
        used for mysql/pgsql
        '''
        raise NotImplementedError

    def _cluster_addr(self, addr = None):
        '''
        return a dict {'itf_name': 'data'}
        '''
        result = {}
        cluster_addr = self.cluster_addr if addr is None else addr
        if not isinstance(cluster_addr, (list,dict)):
            cluster_addr = [cluster_addr]

        for data in cluster_addr:
            itf, addr = data.split(':')
            cluster_addr_name = "ip_%s_%s" % (self.cluster_name, itf)
            ip_params = 'ip="%s" nic="%s"' % (addr, itf)
            result[cluster_addr_name] = (self._resource_primitive(cluster_addr_name,
                                         rsc_class    = "ocf",
                                         rsc_provider = 'heartbeat',
                                         rsc_type     = "IPaddr2",
                                         rsc_params   = ip_params,
                                         rsc_op       = ['monitor interval="30s"']
                                         ))
        return result

    def _cluster_mailto(self, mail_addr = None):
        '''
        configure mail service
        '''
        name = "mailto_%s" % self.cluster_name
        mail_params = "email=%s" % self.cluster_mailto
        primitive = self._resource_primitive(name,
                                             rsc_class = 'ocf',
                                             rsc_provider = 'heartbeat',
                                             rsc_type     = "MailTo",
                                             rsc_params   = mail_params
                                            )
        return name, primitive
                                             
    def _cluster_pingd(self, ipaddr = None):
        '''
        configure pingd service
        '''
        res = "pingd_%s" % self.cluster_name
        pingd_params = 'host_list=%s multiplier=100' % self.cluster_pingd
        primitive = self._resource_primitive(res,
                                             rsc_class = 'ocf',
                                             rsc_provider = 'pacemaker',
                                             rsc_type     = 'pingd',
                                             rsc_params   = pingd_params
                                            )
        clone = 'clone pingdclone %s meta globally-unique=false' % res
        return [primitive, clone]

    def create_config_file(self):
        '''
        create config file (cluster.cfg)
        '''
        return self._cluster_configure()
        
    def cluster_start_res(self):
        '''
        start cluster
        '''
        print('start all resources')
        self._cluster_start_all_resources()

    def cluster_stop_res(self):
        '''
        stop all resources
        '''
        print('stop all resources')
        self._cluster_stop_all_resources()

    def manage(self):
        '''
        used to configure cluster :
            - backup old configuration
            - stopping all running resources
            - erase cluster configuration
            - push the new configuration
        '''
        print("backup conf")
        self._cluster_backup()
        print("stop all resources")
        self._cluster_stop_all_resources()
        print("erase configuration")
        er_data, er_res, er_error = self._cluster_erase_configuration()
        if er_res is not 0:
            raise IOError('impossible to erase configuration : %s', er_data)
        print("configure cluster")
        self._cluster_configure()
        result = self._cluster_push_config()
        if result != 'ok':
            for message in result:
                data = message.split()
                if data[0] != 'WARNING:':
                    print(message)
        return True

    def status(self):
        '''
        return cluster status
        '''
        args = ['crm_mon', '-1']
        data, res, error = self._cluster_command(args)
        for l in data:
            sys.stdout.write(l)
        return True

class DatabaseManagement(object):
    '''
    Used to manage database
    '''
    def __init__(self, ismaster, config):
        """

          ismaster = is this master node (T/F)
          config   = pf-xivo-ha.conf instance
        """
        self.ismaster = ismaster

	# get peer ip
	p   = subprocess.Popen(['ip', 'addr'], stdout=subprocess.PIPE)
        ret = p.wait()
        if ret != 0:
            raise OSError('unable to read local ip addresses')

        data = p.stdout.read()
        if config['nodes']['first_node']['ip'] in data:
            self.local = config['nodes']['first_node']
            self.peer  = config['nodes']['second_node']
        else:
            self.local = config['nodes']['second_node']
            self.peer  = config['nodes']['first_node']

    def initialize(self):
        print "database replication init"
        # authorize postgres ssh key on remote peer
        with open(PG_VAR+'/.ssh/id_rsa.pub') as f:
            pubkey = f.read()

        # prevent ssh from asking to allow remote host
        with open('/etc/ssh/ssh_host_dsa_key.pub') as f:
            hostkey = f.read()
        hostkey = ' '.join(hostkey.split(' ')[:2])

        print "allow remote connection for postgres user on peer. Please enter root password."
        authfile = PG_VAR+'/.ssh/authorized_keys'
        hostfile = PG_VAR+'/.ssh/known_hosts'

        p = subprocess.Popen([
            '/usr/bin/ssh', 
            'root@'+self.peer['ip'],
            "mkdir {pgvar}/.ssh; echo '{pubkey}' > {authfile} && echo '{peername},{peerip} {hostkey}' > {hostfile} && chown -R postgres.postgres {pgvar}/.ssh".format(pgvar=PG_VAR,
							pubkey=pubkey, authfile=authfile,	peername=self.local['name'], peerip=self.local['ip'], hostkey=hostkey, hostfile=hostfile)])
        if p.wait() != 0:
            return

        with open(PG_ETC+'/ha.conf', 'w') as f:
            #TODO: restrict listen_addresses to cluster_itf_data interface
            print >>f, """
listen_addresses  = '*'
wal_level         = 'hot_standby'
archive_mode      = on
archive_command   = 'cd .'  
max_wal_senders   = 10
wal_keep_segments = 5000           # 80 GB required on pg_xlog
hot_standby       = on 
"""

        p = subprocess.Popen(['su','-c','createuser --login --superuser repmgr','postgres'], stderr=subprocess.PIPE)
        p.wait()

        with open(PG_ETC+'/pg_hba.conf', 'r+') as f:
            content = f.read()
            if "# HA\n" not in content:
                f.seek(0, os.SEEK_END)
                print >>f, """
# HA
host     all              repmgr      %s/32         trust
host     all              repmgr      %s/32         trust
host     replication      all         %s/32         trust
""" % (self.local['ip'], self.peer['ip'], self.peer['ip'])

        with open(PG_ETC+'/repmgr.conf', 'w') as f:
            print >>f, """
cluster=xivo
node=%d
conninfo='host=%s user=repmgr dbname=asterisk'
""" % (1 if self.ismaster else 2, self.peer['ip'])

    def update(self):
        raise NotImplementedError

