# -*- coding: UTF-8 -*-

"""A command-line interpreter that interact with provd servers."""

__license__ = """
    Copyright (C) 2011-2012  Avencall

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

import __builtin__
import code
import getpass
import optparse
import os
import re
import readline
import sys
import types
import urllib2
from pprint import pprint
from provd.rest.pycli import pyclient

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8666
DEFAULT_USER = 'admin'
DEFAULT_HISTFILE = os.path.expanduser('~/.provd_pycli_history')
DEFAULT_HISTFILESIZE = 500


# parse command line arguments
parser = optparse.OptionParser(usage='usage: %prog [options] [hostname]')
parser.add_option('-u', '--user', default=DEFAULT_USER,
                  help='user name for server authentication')
parser.add_option('-p', '--password',
                  help='user name for server authentication')
parser.add_option('--port', default=DEFAULT_PORT,
                  help='port number of the REST API')
parser.add_option('-c', '--command',
                  help='specify the command to execute')
parser.add_option('--tests', action='store_true', default=False,
                  help='import the tests module')

opts, args = parser.parse_args()
if not args:
    host = DEFAULT_HOST
else:
    host = args[0]
server_uri = 'http://%s:%s/provd' % (host, opts.port)
if opts.password is None:
    password = getpass.getpass('%s@%s\'s password: ' % (opts.user, host))
else:
    password = opts.password
credentials = (opts.user, password)

## create client object
client = pyclient.new_pycli_provisioning_client(server_uri, credentials)
configs = client.configs()
devices = client.devices()
plugins = client.plugins()
parameters = client.parameters()

## test connectivity
def prompt_continue(err_msg):
    continue_ = raw_input(err_msg + ' Continue anyway ? [y/N] ')
    if len(continue_) == 1 and continue_[0].lower() == 'y':
        return
    else:
        sys.exit(1)

print "Testing server connectivity... ",
try:
    client.test_connectivity()
except urllib2.HTTPError, e:
    print e
    if e.code == 403:
        prompt_continue('Username/password doesn\'t seem to be good.')
    elif e.code == 404:
        prompt_continue('Entry point resource not found.')
    else:
        prompt_continue('Received HTTP %s.' % e.code)
except Exception, e:
    print e
    prompt_continue('Error while connecting.')
else:
    print "ok."


# create help
RAW_HELP_MAP = {
    None: """\
\x1b[1mDescription\x1b[0m
    You can interact with the provd server through 3 top-level objects:
        configs
        devices
        plugins

    Type help(object) (for example help(plugins)) for help about this object.
    
    Type dirr(object) to see all the 'public' attributes of this object.

\x1b[1mExamples\x1b[0m
    Get the list of installable plugins:
    
        plugins.installable()
    
    Synchronize the device 'dev1'
    
        devices['dev1'].synchronize()
    
    Get the raw config of config 'guest'
    
        configs['guest'].get_raw()

\x1b[1mNotes\x1b[0m
    This CLI is a plain python interpreter.
""",
    pyclient.Configs: """\
\x1b[1mDescription\x1b[0m
    Manage the configs.

\x1b[1mExamples\x1b[0m
    Get config 'foo'
    
        configs.get('foo')
    
    Get config 'foo' in raw form
    
        configs.get_raw('foo')
    
    Get config 'foo' as a config object
    
        configs['foo']
    
    List all known config
    
        configs.find()
    
    Add config 'foo'
    
        configs.add({'id': 'foo', 'parent_ids': [],
                     'raw_config.sip.lines.1.proxy_ip': '192.168.32.101'})
    
    Clone config 'foo' to 'bar'
    
        configs.clone('foo', 'bar')
    
    Update config 'foo' (warning: this is a replace operation)
    
        configs.update({'id': 'foo', 'parent_ids': [], 'raw_config': {})
    
    Remove config 'foo'
    
        configs.remove('foo')
""",
    pyclient.Config: """\
\x1b[1mDescription\x1b[0m
    Manage a particular config.
    
    This object is mostly useful if you want to do quick modifications to
    a specific config.

\x1b[1mExamples\x1b[0m
    Set the vlan ID parameter of config 'foo' to 100
    
        configs['foo'].set_config({'vlan.id': '100'})
    
    Unset the vlan ID parameter of config 'foo'
    
        configs['foo'].unset_config('vlan.id')
    
    Set the parent IDs of config 'foo' to 'base'
    
        configs['foo'].set_parents('base')
    
    Get the config 'foo'
    
        configs['foo'].get()
    
    Get the config 'foo' in raw form
    
        configs['foo'].get_raw()
""",
    pyclient.Devices: """\
\x1b[1mDescription\x1b[0m
    Manage the devices.

\x1b[1mExamples\x1b[0m
    Synchronize device 'foo'
    
        devices.synchronize('foo')
    
    Reconfigure device 'foo'
    
        devices.reconfigure('foo')
    
    Get device 'foo'
    
        devices.get('foo')
    
    Get device 'foo' as a device object
    
        devices['foo']
    
    List all known devices which are using 'xivo-aastra-2.6.0.2010' plugin
    
        devices.find({'plugin': 'xivo-aastra-2.6.0.2010'})
    
    Add device 'foo'
    
        devices.add({'id': 'foo', 'mac': '00:11:22:33:44:55'})
    
    Remove device 'foo'
    
        devices.remove('foo')
    
    Update device 'foo' (warning: this is a replace operation, roughly
    equivalent to a remove than an add)
    
        devices.update({'id': 'foo', 'mac': '00:11:22:33:44:55'})
""",
    pyclient.Device: """\
\x1b[1mDescription\x1b[0m
    Manage a particular device.
    
    This object is mostly useful if you want to do quick modifications to
    a specific device. It's always possible to do the same thing via the
    global devices object.
    
\x1b[1mExamples\x1b[0m
    Set the 'plugin' parameter of device 'foo' to 'xivo-aastra-3.2.0.70'
    
        devices['foo'].set({'plugin': 'xivo-aastra-3.2.0.70'})
    
    Unset the 'plugin' parameter of device 'foo'
    
        devices['foo'].unset('plugin')
    
    Synchronize device 'foo'
    
        devices['foo'].synchronize()
    
    Set and synchronize device 'foo'
    
        devices['foo'].set({'config': 'guest'}).synchronize()
    
    Get device 'foo'
    
        devices['foo'].get()
""",
    pyclient.Plugins: """\
\x1b[1mDescription\x1b[0m
    Manage the plugin subsystem.

\x1b[1mExamples\x1b[0m
    Install plugin 'xivo-aastra-2.6.0.2010'
    
        plugins.install('xivo-aastra-2.6.0.2010')
    
    Upgrade plugin 'xivo-aastra-2.6.0.2010'
    
        plugins.upgrade('xivo-aastra-2.6.0.2010')
    
    Uninstall plugin 'xivo-aastra-2.6.0.2010'
    
        plugins.uninstall('xivo-aastra-2.6.0.2010')
    
    Update the installable plugin list
    
        plugins.update()
    
    List the installable plugins
    
        plugins.installable()
    
    List the installed plugins
    
        plugins.installed()
    
    Get the plugin object for plugin 'xivo-aastra-2.6.0.2010'
    
        plugins['xivo-aastra-2.6.0.2010']

    Manage the plugin subsystem parameters
    
        plugins.parameters()
""",
    pyclient.Plugin: """\
\x1b[1mDescription\x1b[0m
    Manage a particular plugin.

\x1b[1mExamples\x1b[0m
    Install plugin-package '6731i-fw'
    
        plugins['xivo-aastra-2.6.0.2010'].install('6731i-fw')
    
    Install all available plugin-packages
    
        plugins['xivo-aastra-2.6.0.2010'].install_all()
    
    Manage this plugin subsystem parameters
    
        plugins['xivo-aastra-2.6.0.2010'].parameters()
""",
    pyclient.Parameters: """\
\x1b[1mDescription\x1b[0m
    Manage parameters of a certain underlying object.

\x1b[1mExamples\x1b[0m
    Get the parameters description
    
        parameters.infos()
    
    Get the value of 'locale' parameter
    
        parameters.get('locale')
    
    Set the value of 'locale' parameter
    
        parameters.set('locale', 'en')
    
    Unset the 'locale' parameter
    
        parameters.unset('locale')
"""
}


class CLIHelp(object):
    def __init__(self, raw_help_map):
        self._help_map = self._build_help_map(raw_help_map)

    @staticmethod
    def _build_help_map(raw_help_map):
        res = {}
        for raw_k, raw_v in raw_help_map.iteritems():
            v = raw_v.rstrip()
            if isinstance(raw_k, types.MethodType):
                res[raw_k.__func__] = v
            else:
                res[raw_k] = v
        return res

    def __call__(self, obj=None):
        help_map = self._help_map
        if obj in help_map:
            print help_map[obj]
        elif type(obj) in help_map:
            print help_map[type(obj)]
        elif isinstance(obj, types.MethodType) and obj.__func__ in help_map:
            print help_map[obj.__func__]
        else:
            print 'No help for object "%s"' % obj

    def __repr__(self):
        return 'Type help() for help, or help(object) for help about object.'


cli_help = CLIHelp(RAW_HELP_MAP)


# define a dirr command
def dirr(obj):
    return list(name for name in dir(obj) if not name.startswith('_'))


# import and initialize the helpers module
import provd.rest.pycli.helpers as helpers
helpers._init_module(configs, devices, plugins)


# import and initialize the tests module
if opts.tests:
    import provd.rest.pycli.plugin_tests as plugin_tests
    plugin_tests._init_module(configs, devices, plugins)


# change interpreter prompt
sys.ps1 = 'provpy> '
sys.ps2 = '....... '


# change display hook
def my_displayhook(value):
    if value is not None:
        __builtin__._ = value
        pprint(value)

sys.displayhook = my_displayhook


# define the CLI global names (without actually inserting them)
cli_globals = {
    'configs': configs,
    'devices': devices,
    'plugins': plugins,
    'parameters': parameters,

    'help': cli_help,
    'python_help': __builtin__.help,

    '__builtins__': __builtin__,
    'dirr': dirr,
    'helpers': helpers,
    'options': pyclient.OPTIONS,
    'pprint': pprint
}

if opts.tests:
    cli_globals['tests'] = plugin_tests


# define completer for readline auto-completion
class Completer(object):
    # This is largely taken from the rlcompleter module
    def __init__(self, namespace):
        if not isinstance(namespace, dict):
            raise TypeError, 'namespace must be a dictionary'

        self.namespace = namespace

    def complete(self, text, state):
        if state == 0:
            if "." in text:
                self.matches = self.attr_matches(text)
            else:
                self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def _callable_postfix(self, val, word):
        if hasattr(val, '__call__'):
            word = word + "("
        return word

    def global_matches(self, text):
        matches = []
        for word, val in self.namespace.items():
            if word.startswith(text) and word != "__builtins__":
                matches.append(self._callable_postfix(val, word))
        return matches

    def attr_matches(self, text):
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        if not m:
            return []
        expr, attr = m.group(1, 3)
        try:
            thisobject = eval(expr, self.namespace)
        except Exception:
            return []

        # get the content of the object, except __builtins__
        words = dirr(thisobject)
        if "__builtins__" in words:
            words.remove("__builtins__")

        if hasattr(thisobject, '__class__'):
            words.extend(get_class_members(thisobject.__class__))
        matches = []
        for word in words:
            if word.startswith(attr) and hasattr(thisobject, word):
                val = getattr(thisobject, word)
                word = self._callable_postfix(val, "%s.%s" % (expr, word))
                matches.append(word)
        return matches

def get_class_members(klass):
    ret = dirr(klass)
    if hasattr(klass, '__bases__'):
        for base in klass.__bases__:
            ret = ret + get_class_members(base)
    return ret

completer = Completer(cli_globals)
readline.set_completer(completer.complete)
readline.parse_and_bind('tab: complete')


# read history file
# purge history from previous raw_input calls, etc
readline.clear_history()
try:
    readline.read_history_file(DEFAULT_HISTFILE)
except EnvironmentError:
    # can't read or no such file
    try:
        # create new file rw only by user
        os.close(os.open(DEFAULT_HISTFILE, os.O_WRONLY, 0o600))
    except OSError:
        pass


# create interpreter and interact with user
if opts.command:
    exec opts.command in cli_globals
else:
    cli = code.InteractiveConsole(cli_globals)
    cli.interact('')


# save history file
readline.set_history_length(DEFAULT_HISTFILESIZE)
try:
    readline.write_history_file(DEFAULT_HISTFILE)
except EnvironmentError:
    print 'warning: could not save history'
