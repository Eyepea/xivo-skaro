# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2010-2011  Avencall

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

import unittest
from provd.servers.tftp.packet import *

RRQ_DGRAM_OPTS_1 = ('\x00\x01filename\x00mode\x00opt1\x00value1\x00',
                    (OP_RRQ, 'filename', 'mode', {'opt1': 'value1'}))
                             
class TestTFTP(unittest.TestCase):
    def test_parse_valid_rrq_dgram_correctly(self):
        self.assertEqual({'opcode': OP_RRQ, 'filename': 'fname', 'mode': 'mode', 'options': {}},
                         parse_dgram('\x00\x01fname\x00mode\x00'))

    def test_parse_invalid_rrq_yield_packeterror(self):
        self.assertRaises(PacketError, parse_dgram, '\x00\x01fname\x00mode')
        self.assertRaises(PacketError, parse_dgram, '')
        self.assertRaises(PacketError, parse_dgram, '\x01')
        self.assertRaises(PacketError, parse_dgram, '\x00\x01')
