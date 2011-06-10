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

import os, subprocess, traceback
import sys
from sys import exit, stderr
import urllib2
from urllib2 import URLError, HTTPError
import json
import fnmatch
import time
import gzip
import contextlib
import re
from optparse import OptionParser

################################################
# Define variables
 
VERBOSE = False
IP_XIVO = "127.0.0.1"
FILE_DELIMITERS = '|'
DEFAULT_OUT_FILE = "/tmp/insert_file_pg_cpoy_%s" % time.strftime('%Y%m%d%H%M%S',time.localtime())

URL_QUEUE = "https://%s/service/ipbx/json.php/private/call_center/queues/" % IP_XIVO
URL_AGENT = "https://%s/service/ipbx/json.php/private/call_center/agents/" % IP_XIVO

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
                    "lastname": "", 
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
               "FROM '%s' DELIMITERS '%s' CSV"  % (DEFAULT_OUT_FILE, FILE_DELIMITERS)

# end of define
##############################################


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
def readlines(directory):
    for file in os.listdir(directory):
        abs_file = os.path.join(directory, file)
        with _open_file(abs_file) as fobj:
            for line in fobj:
                yield line
                

def traitmentline(line, separator='|'):
    rs = line.rstrip().split(separator)
    while len(rs) <= 10:
        rs.append('')
    return rs[:10]


def request_http(url, data=None):    
    try:
        if data is not None:
            data = data.replace(' ', '').replace('\n','')
        req = urllib2.Request(url, data)
        f = urllib2.urlopen(req) 
        return f
    except HTTPError, e: 
        #print e.code
        print e.read()
    except URLError, e:
        print e.reason


def exec_ws():
    for q in LIST_QUEUE:
        f = request_http('%s?act=search&search=%s' % (URL_QUEUE, q))
        if f.code == 204:
            data = json.dumps(DATA_QUEUE) % q
            if VERBOSE:
                print 'JSON:', data
            f = request_http('%s?act=add' % (URL_QUEUE), data)
    for a in LIST_AGENT:
        m = re.search("agent/([0-9]{4})", a, re.I)
        if m is not None:
            data = json.dumps(DATA_AGENT) % (a, m.group(1))
            if VERBOSE:
                print 'JSON:', data
            f = request_http('%s?act=add' % (URL_AGENT), data)
        

def main(directory):
    if not os.access(directory, os.R_OK):
        raise "Can't open directory %s" % directory
    fobj = open(DEFAULT_OUT_FILE,'w')
    for line in readlines(directory):
        linet = traitmentline(line)
        datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime((int(linet[0]))))
        lineoutput = '%s%s' % (datetime, FILE_DELIMITERS) + FILE_DELIMITERS.join(linet[1:]) + '\n'
        fobj.write(lineoutput)
        # build list queue
        LIST_QUEUE.add(linet[2])
        # build list agent
        LIST_AGENT.add(linet[3])
    fobj.close()
    exec_ws()
    try:
        subprocess.check_call(['sudo', '-H', '-u', 'postgres' ,'psql' ,'asterisk', '-c', COMMAND_COPY])
    except (OSError, subprocess.CalledProcessError), e:
        traceback.print_exc()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='mode verbose')
    parser.add_option('-o', '--outfile', action='store_true', dest='output_filename',
                      help='choose out file', default=DEFAULT_OUT_FILE)
    opts, args = parser.parse_args()
    if opts.verbose:
        VERBOSE = True
    if opts.output_filename:
        DEFAULT_OUT_FILE = opts.output_filename
    if len(args) != 1:
        print >>sys.stderr, "usage: %s -v -o <output_filename> <directory>" % ("./qlogtopostgres.py")
        raise sys.exit(1)
    else:
        main(args[0])

