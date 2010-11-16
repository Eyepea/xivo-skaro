# -*- coding: UTF-8 -*-

import unittest

from prov2.servers.tftp.packet import *

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
