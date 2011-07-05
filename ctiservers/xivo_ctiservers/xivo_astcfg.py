# XiVO CTI Server

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

from xivo import anysql
import logging

log = logging.getLogger('astconfig')

## \class AsteriskConfig
# \brief Properties of an Asterisk server
class AsteriskConfig:
    ## \var astid
    # \brief Asterisk String ID

    ## \var ipaddress_webi
    # \brief IP address allowed to send CLI commands

    ##  \brief Class initialization.
    def __init__(self, astid, xca):
        self.astid = astid

        self.userfeatures_db_uri = xca.get('userfeatures_db_uri')
        self.cdr_db_uri = xca.get('cdr_db_uri')

        self.faxcallerid = xca.get('faxcallerid', 'faxcallerid')

        self.userfeatures_db_conn = None
        try:
            if self.userfeatures_db_uri is not None:
                self.userfeatures_db_conn = anysql.connect_by_uri(str(self.userfeatures_db_uri.replace('\/', '/')))
        except Exception:
            log.exception('(init userfeatures_db_conn for %s)' % astid)

        if self.cdr_db_uri == self.userfeatures_db_uri:
            self.cdr_db_conn = self.userfeatures_db_conn
        else:
            self.cdr_db_conn = None
            try:
                self.cdr_db_conn = anysql.connect_by_uri(str(self.cdr_db_uri.replace('\/', '/')))
            except Exception:
                log.exception('(init cdr_db_conn for %s)' % astid)
