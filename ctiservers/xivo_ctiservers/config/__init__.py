#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
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

import ssl

ALARM_DIRECTORY = '/var/lib/pf-xivo-cti-server/alarms'
BUFSIZE_LARGE = 262144
DAEMONNAME = 'ctid'
DEBUG_MODE = False
LOGDAEMONNAME = 'ctid'
LOGFILENAME = '/var/log/pf-xivo-cti-server/daemon.log'
PIDFILE = '/var/run/%s.pid' % DAEMONNAME
PORTDELTA = 0
SSLPROTO = ssl.PROTOCOL_TLSv1
XIVOIP = 'localhost'
XIVO_CONF_FILE = 'http://localhost/cti/json.php/private/configuration'
XIVO_CONF_FILE_DEFAULT = 'file:///etc/pf-xivo/ctiservers/ctiserver_default_configuration.json'
XIVO_CONF_OVER = None

cconf = None
