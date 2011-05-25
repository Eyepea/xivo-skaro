import subprocess

import os

class Tools(object):
    def _cluster_command(self, args = None):
        '''
        command to manage cluster
        _cluster_command(['crm', 'command', 'arg']
        _cluster_command(['crm_verify', '-LV']
        return a turple with (stdout, return code, errors)
        '''
        if args: 
            command = subprocess.Popen(args,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
            error   = command.stderr.__str__()
            result  = command.stdout.readlines()
            ret     = command.wait()
            return result, ret, error
        else:
            raise ValueError

    def _format_string(self, string):
        string = "\t" + string + "\n"
        return string

    def _lsb_status(self, res, expected_state):
        script = '/etc/init.d/%s' % res
        if os.path.isfile(script):
            cmd = [script, 'status']
            result, ret, error = self._cluster_command(cmd)
            if ret is 0:
                state = "started"
            elif ret is 3:
                state = "stopped"
            return state
        else:
            return False
