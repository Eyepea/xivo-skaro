# -*- coding: UTF-8 -*-

import unittest
from provd.operation import *


class TestParseOip(unittest.TestCase):
    def test_state(self):
        oip = parse_oip('state')
        self.assertEqual(None, oip.label)
        self.assertEqual('state', oip.state)
        self.assertEqual(None, oip.current)
        self.assertEqual(None, oip.end)
        self.assertEqual([], oip.sub_oips)

    def test_state_label(self):
        oip = parse_oip('label|state')
        self.assertEqual('label', oip.label)
        self.assertEqual('state', oip.state)
        self.assertEqual(None, oip.current)
        self.assertEqual(None, oip.end)
        self.assertEqual([], oip.sub_oips)
    
    def test_state_current(self):
        oip = parse_oip('state;0')
        self.assertEqual(None, oip.label)
        self.assertEqual('state', oip.state)
        self.assertEqual(0, oip.current)
        self.assertEqual(None, oip.end)
        self.assertEqual([], oip.sub_oips)
        
    def test_state_current_end(self):
        oip = parse_oip('state;0/1')
        self.assertEqual(None, oip.label)
        self.assertEqual('state', oip.state)
        self.assertEqual(0, oip.current)
        self.assertEqual(1, oip.end)
        self.assertEqual([], oip.sub_oips)
        
    def test_state_current_end_label(self):
        oip = parse_oip('label|state;0/1')
        self.assertEqual('label', oip.label)
        self.assertEqual('state', oip.state)
        self.assertEqual(0, oip.current)
        self.assertEqual(1, oip.end)
        self.assertEqual([], oip.sub_oips)
    
    def test_state_sub_state(self):
        oip1 = parse_oip('state1(state11)')
        self.assertEqual(None, oip1.label)
        self.assertEqual('state1', oip1.state)
        self.assertEqual(None, oip1.current)
        self.assertEqual(None, oip1.end)
        self.assertEqual(1, len(oip1.sub_oips))
        
        oip11 = oip1.sub_oips[0]
        self.assertEqual(None, oip11.label)
        self.assertEqual('state11', oip11.state)
        self.assertEqual(None, oip11.current)
        self.assertEqual(None, oip11.end)
        self.assertEqual([], oip11.sub_oips)
    
    def test_state_two_sub_state(self):
        oip1 = parse_oip('state1(state11)(state12)')
        self.assertEqual(None, oip1.label)
        self.assertEqual('state1', oip1.state)
        self.assertEqual(None, oip1.current)
        self.assertEqual(None, oip1.end)
        self.assertEqual(2, len(oip1.sub_oips))
        
        oip11 = oip1.sub_oips[0]
        self.assertEqual(None, oip11.label)
        self.assertEqual('state11', oip11.state)
        self.assertEqual(None, oip11.current)
        self.assertEqual(None, oip11.end)
        self.assertEqual([], oip11.sub_oips)
        
        oip12 = oip1.sub_oips[1]
        self.assertEqual(None, oip12.label)
        self.assertEqual('state12', oip12.state)
        self.assertEqual(None, oip12.current)
        self.assertEqual(None, oip12.end)
        self.assertEqual([], oip12.sub_oips)
    
    def test_complex(self):
        oip1 = parse_oip('label1|state1;1/1(label11|state11;11/11(label111|state111;111/111))(label12|state12;12/12)')
        
        self.assertEqual('label1', oip1.label)
        self.assertEqual('state1', oip1.state, )
        self.assertEqual(1, oip1.current)
        self.assertEqual(1, oip1.end)
        self.assertEqual(2, len(oip1.sub_oips))
        
        oip11 = oip1.sub_oips[0]
        self.assertEqual('label11', oip11.label)
        self.assertEqual('state11', oip11.state, )
        self.assertEqual(11, oip11.current)
        self.assertEqual(11, oip11.end)
        self.assertEqual(1, len(oip11.sub_oips))
        
        oip111 = oip11.sub_oips[0]
        self.assertEqual('label111', oip111.label)
        self.assertEqual('state111', oip111.state, )
        self.assertEqual(111, oip111.current)
        self.assertEqual(111, oip111.end)
        self.assertEqual([], oip111.sub_oips)
        
        oip12 = oip1.sub_oips[1]
        self.assertEqual('label12', oip12.label)
        self.assertEqual('state12', oip12.state, )
        self.assertEqual(12, oip12.current)
        self.assertEqual(12, oip12.end)
        self.assertEqual([], oip12.sub_oips)
