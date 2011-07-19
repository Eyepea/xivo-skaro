#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__   = '$Revision: 0.1 $'
__date__      = '$Date: 2010-06-08 10:41:52 -0400 (mer 08 jun 2010) $'
__copyright__ = 'Copyright (C) 2009-2011 Proformatique'
__author__    = 'Cedric Abunar'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ConfigParser
import contextlib
import fnmatch
import gzip
import json
import os
import re
import subprocess
import sys
import time
import traceback
import urllib2
from optparse import OptionParser
from sys import exit, stderr
from urllib2 import URLError, HTTPError

import psycopg2
from xivo import anysql
from xivo.BackSQL import backpostgresql

################################################
# Define variables

VERBOSE = False
DEBUG = False
IP_XIVO = "127.0.0.1"
FILE_DELIMITERS = '|'
DEFAULT_OUT_FILE = "/tmp/insert_file_pg_copy_%s" % time.strftime('%Y%m%d%H%M%S',time.localtime())

CONF_INI_FILE = '/etc/pf-xivo/stats_accounts.ini'
IPBX_INI_FILE = '/etc/pf-xivo/web-interface/ipbx.ini'
QLOG_DIR = '/var/lib/pf-xivo-web-interface/statistics/qlog'

URL_QUEUE = "https://%s/callcenter/json.php/private/settings/queues/?forcedatabase=%s"
URL_AGENT = "https://%s/callcenter/json.php/private/settings/agents/?forcedatabase=%s"

LIST_QUEUE = set()
LIST_AGENT = set()

DATA_QUEUE ={ "queuefeatures": 
                {
                    "name": "%s", 
                    "context": "default", 
                    "number": "", 
                    "timeout": 0
                },
                "queue": 
                { 
                    "timeoutpriority": "app", 
                    "min-announce-frequency": 60, 
                    "announce-position": "yes", 
                    "announce-position-limit": 5 
                }
            }
DATA_AGENT ={ "agentfeatures": 
                {
                    "firstname": "%s", 
                    "lastname": "%s", 
                    "context": "default", 
                    "number": "%s", 
                    "numgroup": 1, 
                    "autologoff": 0, 
                    "ackcall": "no", 
                    "wrapuptime": 0, 
                    "acceptdtmf": "#", 
                    "enddtmf": "*" 
                },
                "agentoptions": 
                {
                    "maxlogintries": 3 
                }
            }

COMMAND_COPY = "COPY queue_log (time,callid,queuename,agent,event,data1,data2,data3,data4,data5) " \
               "FROM '%s' DELIMITERS '%s' CSV"  %( DEFAULT_OUT_FILE, FILE_DELIMITERS)
               

# end of define
##############################################


def parse_qlog_dir_process():
    global DB_NAME
    global CLIENT
    config = ConfigParser.RawConfigParser()
    with open(CONF_INI_FILE) as fobj:
        config.readfp(fobj)
    list_client = config.sections()
    for client in list_client:
        dir_process = os.path.join(QLOG_DIR, client, 'process')
        if os.access(dir_process, os.R_OK):
            if VERBOSE:
                print 'Processing dirrectory for', client, '...'
            DB_NAME = 'ast_%s' % client
            CLIENT = client
            main(dir_process)
    

class DbManager(object):
    
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.readfp(open(IPBX_INI_FILE))
        db_uri = config.get('general', 'datastorage').strip('"')
        
        self._conn = backpostgresql.connect_by_uri(db_uri)
        self.cursor = self._conn.cursor()
        
    def close(self):
        self._conn.close()
        

def _limit(count):
   # decorator that limit the number of elements returned by a generator
   def aux(fun):
       def aux2(*args, **kwargs):
           n = count
           it = fun(*args, **kwargs)
           while n:
               yield it.next()
               n -= 1
       return aux2
   return aux
        

def _open_file(file):
    if file.endswith('.gz'):
        return contextlib.closing(gzip.open(file))
    else:
        return open(file)


#@_limit(50000)
def readlines(directory, backup=None):
    for file in os.listdir(directory):
        abs_file = os.path.join(directory, file)
        with _open_file(abs_file) as fobj:
            for line in fobj:
                yield line
        if backup is not None:
            newfile = os.path.join(QLOG_DIR, CLIENT, 'backup', file)
            os.rename(abs_file, newfile)


def traitmentline(line, separator='|'):
    rs = line.rstrip().split(separator)
    while len(rs) <= 10:
        rs.append('')
    return rs[:10]


def find_most_recent(directory, partial_file_name=None): 
    # list all the files in the directory
    files = os.listdir(directory) 
    # remove all file names that don't match partial_file_name string
    if partial_file_name is not None:
        files = filter(lambda x: x.find(partial_file_name) > -1, files) 
    # create a dict that contains list of files and their modification timestamps
    name_n_timestamp = dict([(x, os.stat(os.path.join(directory,x)).st_mtime) for x in files]) 
    # return the file with the latest timestamp
    return max(name_n_timestamp, key=lambda k: name_n_timestamp.get(k))


def valid_line(cursor, linet):
    return True
    cursor.execute("SELECT count(time) FROM queue_log "
            "WHERE callid = '%s' "
            "AND queuename = '%s' "
            "AND agent = '%s' "
            "AND event = '%s' LIMIT 1" % (linet[1], linet[2], linet[3], linet[4]))
    
    retval = not cursor.fetchone()
    return retval


def request_http(url, data=None):
    try:
        if data is not None:
            data = data.replace(' ', '').replace('\n','')
        req = urllib2.Request(url, data)
        f = urllib2.urlopen(req) 
        return f
    except HTTPError, e:
        if DEBUG:
            print 'code:', e.code,' response:', e.read()
    except URLError, e:
        if DEBUG:
            print 'code:', e.code,' response:', e.read()


def exec_ws():
    base_url_queue = URL_QUEUE % (IP_XIVO, DB_NAME)
    for q in LIST_QUEUE:
        f = request_http('%s&act=search&search=%s' % (base_url_queue, q))
        if hasattr(f, 'code'):
            if DEBUG:
                print 'code:', f.code,' response:', f.read()
            if f.code == 204:
                data = json.dumps(DATA_QUEUE) % q
                f = request_http('%s&act=add' % (base_url_queue), data)
                if DEBUG:
                    print 'QUEUE ADD JSON:', data
                    #print 'code:', f.code,' response:', f.read()
    base_url_agent = URL_AGENT % (IP_XIVO, DB_NAME)
    for a in LIST_AGENT:
        m = re.search("agent/([0-9]+)", a, re.I)
        if m is not None:
            agent_dir = os.path.join(QLOG_DIR, CLIENT, 'agent');
            number = m.group(1)
            agent_filename = find_most_recent(agent_dir)
            agent_filepath = os.path.join(agent_dir, agent_filename)
            agents = json.load(open(agent_filepath))
            if agents:
                for agent in agents:
                    if number == agent[5]:
                        firstname = agent[3]
                        lastname = agent[4]
                        if VERBOSE:
                            print 'Found agent identity for', a, ':', firstname, lastname
            data = json.dumps(DATA_AGENT) % (firstname, lastname, number)
            f = request_http('%s&act=add' % (base_url_agent), data)
            if DEBUG:
                print 'AGENT ADD JSON:', data
                #print 'code:', f.code,' response:', f.read()


def main(directory):
    if not os.access(directory, os.R_OK):
        raise Exeption("Can't open directory %s" % directory)
    dbman = DbManager()
    fobj = open(DEFAULT_OUT_FILE,'w')
    for line in readlines(directory,True):
        linet = traitmentline(line)
        if valid_line(dbman.cursor, linet):
            datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime((int(linet[0]))))
            lineoutput = '%s%s' % (datetime, FILE_DELIMITERS) + FILE_DELIMITERS.join(linet[1:]) + '\n'
            fobj.write(lineoutput)
            # build list queue
            LIST_QUEUE.add(linet[2])
            # build list agent
            LIST_AGENT.add(linet[3])
    fobj.close()
    dbman.close()
    
    PGCREATEDB = "CREATE DATABASE \"%s\" TEMPLATE tpl_asterisk;" % DB_NAME
    
    try:
        if VERBOSE:
            print 'sudo', '-H', '-u', 'postgres' ,'psql', '-c', PGCREATEDB
        subprocess.check_call(['sudo', '-H', '-u', 'postgres' ,'psql', '-c', PGCREATEDB])
    except:
        pass
    
    exec_ws()
    
    try:
        if VERBOSE:
            print 'sudo', '-H', '-u', 'postgres' ,'psql' ,DB_NAME, '-c', COMMAND_COPY
        subprocess.check_call(['sudo', '-H', '-u', 'postgres' ,'psql' ,DB_NAME, '-c', COMMAND_COPY])
    except (OSError, subprocess.CalledProcessError), e:
        traceback.print_exc()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='mode verbose')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='mode debug')
    parser.add_option('-o', '--outfile', action='store', dest='output_filename',
                      help='choose out file', default=DEFAULT_OUT_FILE)
    parser.add_option('-c', '--client', action='store', dest='output_client',
                      help='choose client')
    opts, args = parser.parse_args()
    if opts.verbose:
        VERBOSE = True
    if opts.debug:
        DEBUG = True
    if opts.output_filename:
        DEFAULT_OUT_FILE = opts.output_filename
    if opts.output_client:
        DB_NAME = 'ast_%s' % opts.output_client
        CLIENT = opts.output_client
        main(os.path.join(QLOG_DIR, CLIENT, 'process'))
    else:
        parse_qlog_dir_process()
    #    print >>sys.stderr, "usage: %s -c <client_name>" % ("./execqlog.py")
    #    raise sys.exit(1)

