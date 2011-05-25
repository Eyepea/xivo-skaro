# -*- coding: UTF-8 -*-

__version__ = "$Revision: 10770 $ $Date: 2011-05-10 18:52:51 +0200 (Tue, 10 May 2011) $"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from xivo_agid import agid
from xivo_agid import objects

logger = logging.getLogger(__name__)

def paging(agi, cursor, args):

    try:
        paging = objects.Paging (agi,
                                 cursor,
                                 args[0])
    except (ValueError, LookupError), e:
        agi.dp_break(str(e))

    paging_line = ''
    paging_opts = ''
    try:
        paging_line = '&'.join(paging.lines)
    except:
        pass


    agi.set_variable('XIVO_PAGING_LINES', paging_line)
    agi.set_variable('XIVO_PAGING_TIMEOUT', paging.timeout)

    if paging.duplex:
            paging_opts = paging_opts + 'd'

    if paging.quiet:
            paging_opts = paging_opts + 'q'

    if paging.record:
            paging_opts = paging_opts + 'r'

    if paging.callnotbusy:
            paging_opts = paging_opts + 's'

    if paging.force_page:
            paging_opts = paging_opts + 'i'

    if paging.announcement_play:
            paging_opts = paging_opts + 'A(%s)' % paging.announcement_file

    if not paging.default_group:
            paging_opts = paging_opts + 'n'

    agi.set_variable('XIVO_PAGING_OPTS', paging_opts)

agid.register(paging)
