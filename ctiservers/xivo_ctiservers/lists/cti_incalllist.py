# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision: 10532 $'
__date__      = '$Date: 2011-04-07 15:00:27 +0200 (Thu, 07 Apr 2011) $'
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
from xivo_ctiservers.cti_anylist import AnyList

log = logging.getLogger('incalllist')

class IncallList(AnyList):
    def __init__(self, newurls = [], useless = None):
        self.anylist_properties = { 'name' : 'incall',
                                    'urloptions' : (1, 5, True) }
        AnyList.__init__(self, newurls)
        return
    
    def update(self):
        ret = AnyList.update(self)
        # self.reverse_index = {}
        return ret
