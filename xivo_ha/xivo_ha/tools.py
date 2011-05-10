import subprocess

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

