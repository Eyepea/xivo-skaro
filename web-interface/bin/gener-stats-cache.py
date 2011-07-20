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

import os
import glob
import ConfigParser
import urllib2
import traceback
import subprocess

from xivo import anysql
from xivo.BackSQL import backpostgresql
from optparse import OptionParser
from urllib2 import URLError, HTTPError

XIVO_INI_FILE = '/etc/pf-xivo/web-interface/xivo.ini'
WS_URI_GENERCACHE = '/statistics/json.php/private/call_center/genercache'
STATS_CACHE_DIR = '/var/lib/pf-xivo-web-interface/statistics/cache'
LIST_TYPE = ['queue','agent','period','incall']


class DbManager(object):
    
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.readfp(open(XIVO_INI_FILE))
        db_uri = config.get('general', 'datastorage').strip('"')
        
        self._conn = backpostgresql.connect_by_uri(db_uri)
        self.cursor = self._conn.cursor()
        
    def close(self):
        self.cursor.close()
        self._conn.close()

        
def request_http(url, data=None):
    try:
        if data is not None:
            data = data.replace(' ', '').replace('\n','')
        req = urllib2.Request(url, data)
        return urllib2.urlopen(req)
    except HTTPError, e:
        print ''
        
        
def main():
    dbman = DbManager()
    dbman.cursor.execute("SELECT * FROM stats_conf")    
    list_conf = dbman.cursor.fetchall()
    dbman.close()
    for conf in list_conf:
        id = conf[0]
        print 'Generation cache for configuration %s in progress...' % conf[1]
        for root, dirs, files in os.walk(os.path.join(STATS_CACHE_DIR, str(id))):
            for dir in dirs:
                os.chown(os.path.join(root, dir), 33, 33)
            for file in files:
                os.chown(os.path.join(root, file), 33, 33)         
        for type in LIST_TYPE:
            qry = 'idconf=%d&type=%s&erase=%s' % (id, type, ERASE)
            try:
                script = '/usr/share/pf-xivo-web-interface/bin/pf-xivo-web-interface-update-stats-cache'
                print 'called script: %s %s' % (script, qry)
                subprocess.call(['php', script, qry])
            except (OSError, subprocess.CalledProcessError), e:
                traceback.print_exc()
                
            continue;
                
            qry = '?act=generbyidconf&idconf=%d&type=%s&erase=%s' % (id, type, ERASE)
            url = 'https://127.0.0.1%s%s' % (WS_URI_GENERCACHE, qry)
            print 'Request: %s' % url
            print 'Generation cache for type %s in progress..' % type
            f = request_http(url)
            print "response..."
            try:
                #print 'response:', f.read()
                for line in f:
                    print line.rstrip()
                if hasattr(f, 'code') and DEBUG:
                    print 'code:', f.code
            finally:
                f.close()
            


if __name__ == '__main__':
    DEBUG = False
    ERASE = 0
    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='mode debug')
    parser.add_option('-e', '--erase', action='store_true', dest='erase',
                      help='mode erase')
    parser.add_option('-c', '--client', action='store', dest='output_client',
                      help='client')
    parser.add_option('-i', '--idconf', action='store', dest='output_idconf',
                      help='idconf')
    opts, args = parser.parse_args()
    if opts.debug:
        DEBUG = True
    if opts.erase:
        ERASE = 1
    if opts.output_client:    
        client = opts.client
    if opts.output_idconf:    
        idconf = opts.idconf
    main()
