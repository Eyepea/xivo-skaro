__version__ = "$Revision: 2 $ $Date: 2009-03-18 02:19:22 +0100 (Wed, 18 Mar 2009) $"
__license__ = """
    Copyright (C) 2009  Proformatique <technique@proformatique.com>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os
import subprocess
import logging
import re
from time import strftime as _strftime
from logging.handlers import SysLogHandler

def _init_hasyslog():
    if not HA_LOGFACILITY:
        return None

    syslog = SysLogHandler("/dev/log", HA_LOGFACILITY)
    syslog.setFormatter(logging.Formatter("%s: %%(message)s" % HA_LOGTAG))
    root_logger.addHandler(syslog)

def _init_halog():
    if not HA_LOGFILE or not os.path.isfile(HA_LOGFILE):
        return

    class HALogFilter(logging.Filter):
        def filter(self, record):
            return record.levelno != logging.DEBUG

    halog = logging.FileHandler(HA_LOGFILE)
    halog.setFormatter(logging.Formatter("%s: %%(asctime)s %%(levelname)s: %%(message)s" % HA_LOGTAG, HA_DATEFMT))
    halog.addFilter(HALogFilter())
    root_logger.addHandler(halog)

def _init_hadebug():
    if not HA_DEBUGLOG or not os.path.isfile(HA_DEBUGLOG):
        return

    debuglog = logging.FileHandler(HA_DEBUGLOG)
    debuglog.setFormatter(logging.Formatter("%s: %%(asctime)s %%(levelname)s: %%(message)s" % HA_LOGTAG, HA_DATEFMT))
    root_logger.addHandler(debuglog)

def _get_log_facility():
    facility = os.getenv('HA_LOGFACILITY')

    if facility is None:
        return
    elif not facility.isdigit():
        facility = facility.lower()
        if facility in SysLogHandler.facility_names:
            return SysLogHandler.facility_names[facility]
        else:
            return

    facility = int(facility)

    if facility in SysLogHandler.facility_names.values():
        return facility

def _get_log_priority(priority):
    if isinstance(priority, basestring):
        if not priority.isdigit():
            priority = priority.upper()
        else:
            priority = int(priority)

    if priority in ('DEBUG', logging.DEBUG):
        return logging.DEBUG
    elif priority in ('INFO', logging.INFO):
        return logging.INFO
    elif priority in ('WARN', 'WARNING', logging.WARNING):
        return logging.WARNING
    elif priority in ('ERR', 'ERROR', logging.ERROR):
        return logging.ERROR
    elif priority in ('CRIT', 'CRITICAL', logging.CRITICAL):
        return logging.CRITICAL

    return logging.NOTSET

def is_root():
    return os.getuid() == 0

def log(priority, msg):
    return ha_log(priority, msg)

def ha_debug(msg):
    return ha_log(logging.DEBUG, msg)

def ha_uuid():
    try:
        res = subprocess.Popen([HA_CRMUUID], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    return res.stdout.read().strip()

def ha_master_uname():
    try:
        res = subprocess.Popen([HA_CRMADMIN, '-D'], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return
    
    if res.wait():
        return

    re_master = re.match(r'^[^:]+:\s+(.+)\s*$', res.stdout.readline())

    if re_master:
        return re_master.group(1).strip()

def ha_node_uuid(uname):
    if not isinstance(uname, basestring):
        return

    try:
        res = subprocess.Popen([HA_CRMADMIN, '-N'], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    esc_uname = re.escape(uname)

    for line in res.stdout.readlines():
        re_uuid = re.match(r'^[^:]+:\s+'+esc_uname+'\s+\(([a-f0-9\-]+)\)$', line)

        if re_uuid:
            return re_uuid.group(1).strip()

def ha_node_uname(uuid):
    if not isinstance(uuid, basestring):
        return

    try:
        res = subprocess.Popen([HA_CRMADMIN, '-N'], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    esc_uuid = re.escape(uuid)

    for line in res.stdout.readlines():
        re_uname = re.match(r'^[^:]+:\s+(.+)\s+\('+esc_uuid+'\)$', line)

        if re_uname:
            return re_uname.group(1).strip()

def ha_node_status(uname):
    if not isinstance(uname, basestring):
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'nodestatus', uname], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    return res.stdout.readline()

def ha_nodes_uname_except(uname):
    if not isinstance(uname, basestring):
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'listnodes', '-n'], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    xlist = []

    for line in res.stdout.readlines():
        node = line.strip()
        if node and uname != node:
            xlist.append(node)

    if not xlist:
        return

    return tuple(xlist)

def ha_node_status(uname):
    """ Return node status: 'active' or 'dead' """
    if not isinstance(uname, basestring):
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'nodestatus', uname], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait() not in [0, 1]:
        return

    return res.stdout.readline()[:-1]

def ha_listhblinks(uname):
    if not isinstance(uname, basestring):
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'listhblinks', uname], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    return tuple([
        line.strip()
        for line in res.stdout.readlines()
        if line.strip()
    ])

def ha_linkstatus(uname, link):
    links = ha_listhblinks(uname)

    if not links or link not in links:
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'hblinkstatus', uname, link],
                               stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if not res.wait() and res.stdout.readline().strip() == 'up':
        return True

    return False

def ha_listhbuplinks(uname):
    links = ha_listhblinks(uname)

    if not links:
        return

    try:
        res = subprocess.Popen([HA_CLSTATUS, 'listhblinks', uname], stdout=subprocess.PIPE)
    except OSError, e:
        sys.stderr.write("%s\n" % str(e))
        return

    if res.wait():
        return

    xlist = []

    for line in res.stdout.readlines():
        link = line.strip()

        if not link:
            continue

        try:
            res1 = subprocess.Popen([HA_CLSTATUS, 'hblinkstatus', uname, link],
                                    stdout=subprocess.PIPE)
        except OSError, e:
            sys.stderr.write("%s\n" % str(e))
            return

        if not res1.wait() and res1.stdout.readline().strip() == 'up':
            xlist.append(link)

    if not xlist:
        return

    return tuple(xlist)

def ha_log(priority, msg):
    try:
        msg = str(msg)
    except ValueError:
        return

    priority = _get_log_priority(priority)

    if HA_LOGD == 'yes':
        listargs = ['ha_logger', '-t', HA_LOGTAG]

        if priority == logging.DEBUG:
            listargs.extend(['-D', 'ha-debug'])

        listargs.append(msg)

        try:
            if subprocess.call(listargs) == 0:
                return True
        except OSError, e:
            sys.stderr.write("%s\n" % str(e)) 

    root_logger.log(priority, msg)

    if HA_DEBUGLOG or priority != logging.DEBUG:
        return

    format = "%s\t%s%s"

    if HA_LOGFACILITY and not os.getenv('HA_LOGFACILITY').isdigit():
        format += ":\t%s" % os.getenv('HA_LOGFACILITY')

    sys.stderr.write((format + "\n") % (HA_LOGTAG, _strftime(HA_DATEFMT), msg))

def ha_pseudo_resource(res_string, op, tracking_file=None):
    if not isinstance(res_string, basestring):
        if op == 'status':
            return 4
        else:
            return ERR_ARGS
    elif not isinstance(tracking_file, basestring) \
    or not os.access(os.path.dirname(tracking_file), os.W_OK):
        tracking_file = os.path.join(HA_RSCTMP, res_string)

    if op in ('start', 'restart', 'reload'):
        try:
            f = open(tracking_file, 'w')
            f.close()
        except OSError, e:
            log(logging.ERROR, str(e))
            return ERR_GENERIC
    elif op == 'stop':
        try:
            os.unlink(tracking_file)
        except OSError:
            pass
    elif op in ('status', 'monitor'):
        if os.path.isfile(tracking_file):
            return SUCCESS
        elif op == 'status':
            return 3
        else:
            return NOT_RUNNING
    elif op == 'print':
        return tracking_file
    else:
        return ERR_UNIMPLEMENTED

    return SUCCESS


SUCCESS             = 0
ERR_GENERIC         = 1
ERR_ARGS            = 2
ERR_UNIMPLEMENTED   = 3
ERR_PERM            = 4
ERR_INSTALLED       = 5
ERR_CONFIGURED      = 6
NOT_RUNNING         = 7
RUNNING_MASTER      = 8
FAILED_MASTER       = 9

ROOT                = os.getenv('OCF_ROOT', '/usr/lib/ocf')
RES_INST            = os.getenv('OCF_RESOURCE_INSTANCE', '')

HA_SBIN_DIR         = os.getenv('HA_SBIN_DIR', '/usr/sbin')
HA_BIN_DIR          = os.getenv('HA_BIN_DIR', '/usr/bin')
HA_RSCTMP           = os.getenv('HA_RSCTMP', '/var/run/heartbeat/rsctmp')
HA_CRMUUID          = os.path.join(HA_SBIN_DIR, 'crm_uuid')
HA_CRMADMIN         = os.path.join(HA_SBIN_DIR, 'crmadmin')
HA_CLSTATUS         = os.path.join(HA_BIN_DIR, 'cl_status')
HA_LOGD             = os.getenv('HA_LOGD')
HA_LOGFILE          = os.getenv('HA_LOGFILE')
HA_DEBUGLOG         = os.getenv('HA_DEBUGLOG')
HA_LOGFACILITY      = _get_log_facility()
HA_DATEFMT          = os.getenv('HA_DATEFMT', '%Y/%m/%d_%T ')
HA_LOGTAG           = "%s[%s]" % (os.path.basename(sys.argv[0]), os.getpid())

os.putenv('OCF_CHECK_LEVEL', os.getenv('OCF_RESKEY_OCF_CHECK_LEVEL', '0'))

if not os.environ.has_key('OCF_RESOURCE_TYPE'):
    os.putenv('OCF_RESOURCE_TYPE', os.path.basename(sys.argv[0]))

if len(sys.argv) > 1 and sys.argv[1] == 'meta-data':
    os.putenv('OCF_RESOURCE_INSTANCE', 'undef')

logging.raiseExceptions = 0
root_logger = logging.getLogger('') # pylint: disable-msg=C0103
root_logger.setLevel(logging.NOTSET)

_init_hasyslog()
_init_halog()
_init_hadebug()
