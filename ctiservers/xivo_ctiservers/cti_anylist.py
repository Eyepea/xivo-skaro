# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011  Avencall
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
import cti_urllist

log = logging.getLogger('anylist')

class AnyList:
    def __init__(self, newurls):
        self.commandclass = None
        self.requested_list = {}
        self.keeplist = {}
        self.__clean_urls__()
        self.__add_urls__(newurls)
        return

    def update(self):
        lstadd = []
        lstdel = []
        lstchange = {}
        oldlist = self.keeplist
        newlist = {}

        # Get new list from Web services.
        for url, urllist in self.requested_list.iteritems():
            gl = urllist.getlist(* self.anylist_properties['urloptions'])
            if gl == 2:
                tmplist = getattr(self.commandclass, self.getter)(urllist.jsonreply)
                newlist.update(tmplist)

        # Update computed fields, if any.
        self.update_computed_fields(newlist);

        # Compare old (self.keeplist) and new (newlist) list:
        # Compute the differences and update the current list.
        for a, b in newlist.iteritems():
            if a not in oldlist:
                self.keeplist[a] = b
                lstadd.append(a)
            else:
                oldfull = self.keeplist[a]
                if b != oldfull:
                    keywords = []
                    for bk, bv in b.iteritems():
                        oldval = self.keeplist[a][bk]
                        if bv != oldval:
                            self.keeplist[a][bk] = bv
                            keywords.append(bk)
                    if keywords:
                        lstchange[a] = keywords
        for a, b in oldlist.iteritems():
            if a not in newlist:
                lstdel.append(a)

        # Remove old items.
        for a in lstdel:
            del self.keeplist[a]

        if len(lstadd) > 0:
            log.info('%d new %s from %s' % (len(lstadd),
                                            self.anylist_properties['name'],
                                            self.requested_list.keys()))
        if len(lstdel) > 0:
            log.info('%d old %s from %s' % (len(lstdel),
                                            self.anylist_properties['name'],
                                            self.requested_list.keys()))
        return { 'add' : lstadd,
                 'del' : lstdel,
                 'change' : lstchange }

    def update_computed_fields(self, newlist):
        # "Virtual" function
        # You should reimplement it if the list items contains fields
        # that depends on other fields. See MeetmeList for an example.
        pass

    def setcommandclass(self, commandclass):
        self.commandclass = commandclass
        return

    def setgetter(self, getter):
        self.getter = getter
        return

    def __clean_urls__(self):
        self.requested_list = {}
        return

    def __add_urls__(self, newurls):
        for url in newurls:
            if url not in self.requested_list:
                self.requested_list[url] = cti_urllist.UrlList(url)
        return

    def setandupdate(self, newurls):
        self.__add_urls__(newurls)
        if len(self.requested_list) == 0:
            return
        self.update()
        return
