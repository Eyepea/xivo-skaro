# -*- coding: utf-8 -*-

__license__ = """
    Copyright (C) 2008-2010  Avencall

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

def agent_get_options(agi, cursor, args):
    agi.set_variable('XIVO_AGENTEXISTS', 0)

    try:
        number = str(args[0])

        if number.startswith('*'):
            agent = objects.Agent(agi, cursor, xid=number[1:])
        else:
            agent = objects.Agent(agi, cursor, number=number)
    except (LookupError, IndexError), e:
        agi.verbose(str(e))
        return

    options = ""

    if agent.silent:
        options += "s"

    agi.set_variable('XIVO_AGENTEXISTS', 1)
    agi.set_variable('XIVO_AGENTPASSWD', agent.passwd)
    agi.set_variable('_XIVO_AGENTID', agent.id)
    agi.set_variable('_XIVO_AGENTNUM', agent.number)
    agi.set_variable('_XIVO_AGENTOPTIONS', options)

    # get agent lang
    lang = agent.language
    if lang is None or len(lang) == 0:
        userid = agi.get_variable('XIVO_USERID')
        if userid:
            try:                
                caller = objects.User(agi, cursor, int(userid))
                masterline = objects.MasterLineUser(agi, cursor, int(userid))
                lang = caller.language    

                # get channel default lang
                if lang is None or len(lang) == 0:
                    static = objects.Static(cursor, masterline.line['protocol'])
                    lang = static.language                                        

            except (ValueError, LookupError), e:
                pass

    if lang is None or len(lang) == 0:
        # setting default value
        lang = 'fr_FR'

    agi.set_variable('_XIVO_AGENTLANGUAGE', lang)

agid.register(agent_get_options)
