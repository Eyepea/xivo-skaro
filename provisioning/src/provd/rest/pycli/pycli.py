# -*- coding: UTF-8 -*-

"""A command-line interpreter that interact with provisioning servers.

Note that this module is made to be run as 'python -i ...', i.e. the
python interpreter is the command-line interpreter.

"""

__version__ = "$Revision$ $Date$"
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


# TODO test credentials and server reachability at start
# XXX add some 'utility function' to do common high-level task; for example
#     resynchronizing every device


def init():
    import getpass
    import optparse
    import sys
    from provd.rest.pycli.pyclient import new_pycli_provisioning_client
    
    _DEFAULT_SERVER_URI = 'http://localhost:8081/provd'
    
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', dest='user',
                      help='user name for server authentication')
    
    opts, args = parser.parse_args()
    if not args:
        server_uri = _DEFAULT_SERVER_URI
    elif len(args) == 1:
        server_uri = args[0]
    else:
        print >>sys.stderr, 'Need at most 1 argument, received %d' % len(args)
        exit(1)
    
    if opts.user:
        passwd = getpass.getpass('"%s" password: ' % server_uri)
        credentials = (opts.user, passwd)
    else:
        credentials = None
    
    sys.ps1 = 'provpy> '
    sys.ps2 = '...... '
    return new_pycli_provisioning_client(server_uri, credentials)


class ProvHelp(object):
    def __repr__(self):
        # TODO
        return 'good try, but there is no help right now...'


# put some names in global namespace
from pprint import pprint
client = init()
help = ProvHelp()
python_help = __builtins__.help
# XXX insert these objects into global namespace since they must be here to
#     do anything useful ?
cfg_mgr = client.config_manager
dev_mgr = client.device_manager
pg_mgr = client.plugin_manager

# cleanup global namespace
for name in ['init', 'ProvHelp']:
    del globals()[name]
del name
