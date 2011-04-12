#!/usr/bin/env python

import subprocess
from time import localtime, strftime

class ClusterResourceManager(object):
    def __init__(self, backup_directory = "/tmp"):
        self.backup_directory = backup_directory

    def _backup_old_configuration(self, directory):
        args       = ['cibadmin', '--query']
        time       = strftime("%Y%m%d-%H%M%S", localtime())
        old_config = self._cluster_command(args)
        old_config_file = "%s/cib-%s.xml" % (directory, time)
        with open(old_config_file, 'w') as file_:
            try:
                for line in old_config:
                    file_.write(line)
            except:
                IOError("impossible to backup the actual configuration")
        return old_config_file

    def _check_cluster_status(self):
        '''
        check with crm_verify cluster state
        '''
        return True

    def _cluster_command(self, args = []):
        '''
        use crm to manage cluster
        '''
        if args.__len__() is not 0:
            command = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
            error   = command.stderr.__str__()
            result  = command.stdout.readlines()
            if error is not 'None':
                return result
            else:
                raise OSError(error) 
        else:
            raise ValueError, "You have to provide command (args = %s)" % args


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
        # TODO create a config file : http://www.clusterlabs.org/doc/crm_cli.html (cf 3, cluster configuration)
        #stonith     = ["crm", "configure", "property", "stonith-enabled=false"]
        #quorum      = ["crm", "configure", "property", "no-quorum-policy=ignore"]
        #stickiness  = ["crm", "configure", "rsc_defaults", "resource-stickiness=100"]

        #for cmd in (stonith, quorum, stickiness):
        #    self._cluster_command(cmd)
        pass

    def _cluster_configure_service(self):
        '''
        add service in cluster
        '''
        pass

    def _rollback(self):
        '''
        rollback
        '''
        pass

    def __init__(self):
        pass

    def initialize(self):
        self._backup_old_configuration()
        if self._check_cluster_status():
            # pass globals options
            self._cluster_global_option()
            self._cluster_configure_service()
            return True
        else:
            self._rollback()

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
