# XiVO CTI Server
# vim: set fileencoding=utf-8

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011 Proformatique'
__author__    = 'Corentin Le Gall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import urllib2
import sys
import cjson

from xivo_ctiservers import cti_directories

log = logging.getLogger('cti_config')

class Config:
    def __init__(self, * urilist):
        self.urilist = urilist
        self.ctxlist = {}
        self.dpylist = {}
        self.dirlist = {}

        self.update()
        return

    def update(self):
        # the aim of the urilist would be to handle the URI's one after the other
        # when there is a reachability issue (like it can happen in first steps ...)
        self.update_uri(self.urilist[0])
        return

    def update_uri(self, uri):
        if uri.find('json') < 0:
            return
        if uri.find(':') < 0:
            return

        response = urllib2.urlopen(uri)
        self.json_config = response.read().replace('\/', '/')
        self.xc_json = cjson.decode(self.json_config)

        for profile, profdef in self.xc_json['xivocti']['profiles'].iteritems():
            if profdef['xlets']:
                for xlet_attr in profdef['xlets']:
                    if 'N/A' in xlet_attr:
                        xlet_attr.remove('N/A')
                    if ('tab' or 'tabber') in xlet_attr:
                        del xlet_attr[2]
                    if xlet_attr[1] == 'grid':
                        del xlet_attr[2]

        try:
            self.setdirconfigs()
        except:
            log.exception('setdirconfigs')
        return

    def setdirconfigs(self):
        for dirid, dirdet in self.xc_json['directories'].iteritems():
            if dirid not in self.dirlist:
                self.dirlist[dirid] = cti_directories.Directory(dirid)
            self.dirlist[dirid].update(dirdet)
        for dpyid, dpydet in self.xc_json['displays'].iteritems():
            if dpyid not in self.dpylist:
                self.dpylist[dpyid] = cti_directories.Display()
            self.dpylist[dpyid].update(dpydet)
        for contextname, contextdef in self.xc_json['contexts'].iteritems():
            if contextname not in self.ctxlist:
                self.ctxlist[contextname] = cti_directories.Context()
            self.ctxlist[contextname].update(contextdef)

    def getconfig(self, key = None):
        if key:
            ret = self.xc_json.get(key)
        else:
            ret = self.xc_json
        return ret
