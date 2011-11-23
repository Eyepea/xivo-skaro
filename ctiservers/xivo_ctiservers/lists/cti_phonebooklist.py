# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date: 2011-04-06 17:20:05 +0200 (Wed, 06 Apr 2011) $'
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
from xivo_ctiservers.cti_anylist import AnyList

log = logging.getLogger('phonebook')

class PhonebookList(AnyList):
    def __init__(self, newurls = [], useless = None):
        self.anylist_properties = { 'name' : 'phonebook',
                                    'urloptions' : (1, 5, True)}
        AnyList.__init__(self, newurls)
        self.commandclass = self
        self.getter = '_getphonebook'

    def setcommandclass(self, commandclass):
        # WARNING: this is a hack, i.e. we are overriding the setcommandclass
        # so that it's not possible to change the commandclass, and this
        # breaks with the expected behaviour of the setcommandclass method
        log.debug("In PhonebookList: ignoring setcommandclass")

    def setgetter(self, getter):
        # WARNING: this is a hack, see setcommandclass for more info.
        log.debug("In PhonebookList: ignoring setgetter")

    def _getphonebook(self, jsonreply):
        pblist = {}
        for pitem in jsonreply:
            pbitem = {}
            for i1, v1 in pitem.iteritems():
                if isinstance(v1, dict):
                    for i2, v2 in v1.iteritems():
                        if isinstance(v2, dict):
                            for i3, v3 in v2.iteritems():
                                idx = '.'.join([i1, i2, i3])
                                pbitem[idx] = v3
                        else:
                            idx = '.'.join([i1, i2])
                            pbitem[idx] = v2
                else:
                    pbitem[i1] = v1
            myid = pbitem.get('phonebook.id')
            pblist[myid] = pbitem
        return pblist
