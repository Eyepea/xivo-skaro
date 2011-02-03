# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
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

import unittest
from prov.sip import Parameters, URI 


class TestURIParameters(unittest.TestCase):
    def test_parse_empty_string(self):
        obj = Parameters.parse('')
        self.assertEqual('', str(obj))
    
    def test_parse_one_namevalue_param_string(self):
        obj = Parameters.parse(';foo=bar')
        transport_param = obj.get('foo')
        self.assertEqual('foo', transport_param.name)
        self.assertEqual('bar', transport_param.value)
        self.assertEqual(';foo=bar', str(obj))
    
    def test_parse_one_name_param_string(self):
        obj = Parameters.parse(';foo')
        foo_param = obj.get('foo')
        self.assertEqual('foo', foo_param.name)
        self.assertEqual(';foo', str(obj))
    
    def test_parse_zero_length_param_raise_error(self):
        self.assertRaises(ValueError, Parameters.parse, ';')
        self.assertRaises(ValueError, Parameters.parse, ';foo;')
        self.assertRaises(ValueError, Parameters.parse, ';;foo')


class TestURI(unittest.TestCase):
    def test_parse_exemple1(self):
        tc = 'sip:alice:secretword@atlanta.com;transport=tcp'
        obj = URI.parse(tc)
        self.assertEqual('sip', obj.scheme)
        self.assertEqual('alice', obj.user)
        self.assertEqual('secretword', obj.password)
        self.assertEqual('atlanta.com', obj.host)
        self.assertEqual(5060, obj.port)
        self.assertEqual('transport', obj.uri_params.get('transport').name)
        self.assertEqual('tcp', obj.uri_params.get('transport').value)

    def test_parse_exemple2(self):
        tc = 'sips:alice@atlanta.com'
        obj = URI.parse(tc)
        self.assertEqual('sips', obj.scheme)
        self.assertEqual('alice', obj.user)
        self.assertEqual(None, obj.password)
        self.assertEqual('atlanta.com', obj.host)
        self.assertEqual(5061, obj.port)
        self.assertNotEqual(None, obj.uri_params)
    
    def test_parse_exemple3(self):
        tc = 'sip:+1-212-555-1212:1234@gateway.com;user=phone'
        obj = URI.parse(tc)
        self.assertEqual('sip', obj.scheme)
        self.assertEqual('+1-212-555-1212', obj.user)
        self.assertEqual('1234', obj.password)
        self.assertEqual('gateway.com', obj.host)
        self.assertEqual(5060, obj.port)
        self.assertEqual('user', obj.uri_params.get('user').name)
        self.assertEqual('phone', obj.uri_params.get('user').value)

    def test_parse_exemple4(self):
        tc = 'sip:foo:bar@127.0.0.1:5061;foo=bar;foobar'
        obj = URI.parse(tc)
        self.assertEqual('sip', obj.scheme)
        self.assertEqual('foo', obj.user)
        self.assertEqual('bar', obj.password)
        self.assertEqual('127.0.0.1', obj.host)
        self.assertEqual(5061, obj.port)
        self.assertEqual('foo', obj.uri_params.get('foo').name)
        self.assertEqual('bar', obj.uri_params.get('foo').value)
        self.assertEqual('foobar', obj.uri_params.get('foobar').name)
