# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2011 Proformatique'

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

log = logging.getLogger('parkinglotlist')

class ParkinglotList(AnyList):
    def __init__(self, newurls = [], useless = None):
        self.anylist_properties = { 'name' : 'parkinglot',
                                    'urloptions' : (0,0,False)
                                    }
        AnyList.__init__(self, newurls)
        return

    def set_default_parking(self, default_parking):
        """
        Set the default parkinglot info since it's not going to be on the
        updates from the webservices
        """
        self.default_parking = default_parking

    def update(self):
        """
        Since the parking from features.conf is not returned by the webservice
        we have to add it manually after each update
        """
        if '0' in self.keeplist:
            should_add_default = False
        else:
            should_add_default = True
        ret = AnyList.update(self)
        if 'del' in ret and self.default_parking['id'] in ret['del']:
            ret['del'].pop(int(self.default_parking['id']))
            if len(ret['del']) == 0:
                ret.pop('del')
        if should_add_default:
            self.keeplist['0'] = self.default_parking
            ret['add'].append('0')
        return ret
