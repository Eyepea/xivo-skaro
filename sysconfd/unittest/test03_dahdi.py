#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""
import unittest, cjson, pprint
import sysconfd_client

class TestDahdi(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	def test_01_infos(self):
		"""Get spans info. sample:
					{'TE2/0': [{'alarms': ['RED', 'LFA'],
							# channels range
          	  'channels': [1, 32],
            	'config': {'coding': 'HDB3',
              	         'coding_opts': ['AMI', 'HDB3'],
                	       'framing': None,
                  	     'framing_crc4': True,
                    	   'framing_opts': ['CCS', 'CRC4'],
	                       'lbo': 0,
  	                     'syncsrc': 0},
    	        'description': 'T2XXP (PCI) Card 0 Span 1',
      	      'devicetype': 'Wildcard TE205P (4th Gen)',
        	    'irq': 16,
          	  'manufacturer': 'Digium',
            	'name': 'TE2/0/1',
  	          'signalling': 'E1',
	            'spanno': 1,
  	          'type': 'PRI'},
    	       {'alarms': ['RED', 'LFA'],
      	      'channels': [32, 63],
        	    'config': {'coding': 'HDB3',
          	             'coding_opts': ['AMI', 'HDB3'],
            	           'framing': 'CCS',
              	         'framing_crc4': True,
                	       'framing_opts': ['CCS', 'CRC4'],
                  	     'lbo': 0,
                    	   'syncsrc': 0},
	            'description': 'T2XXP (PCI) Card 0 Span 2',
  	          'devicetype': 'Wildcard TE205P (4th Gen)',
    	        'irq': 16,
      	      'manufacturer': 'Digium',
        	    'name': 'TE2/0/2',
  	          'signalling': 'E1',
          	  'spanno': 2,
            	'type': 'PRI'}],
					{'B4/0': [{'alarms': ['RED'],
          		'channels': [71, 73],
		          'config': {'coding': 'AMI',
                  	    'coding_opts': ['B8ZS', 'AMI', 'HDB3'],
                    	  'framing': 'CCS',
	                      'framing_crc4': False,
  	                    'framing_opts': ['ESF', 'D4', 'CCS', 'CRC4'],
    	                  'lbo': 0,
      	                'syncsrc': 0},
    	       'description': 'B4XXP (PCI) Card 0 Span 1',
      	     'devicetype': 'Wildcard B410P',
        	   'irq': 18,
	           'manufacturer': 'Digium',
  	         'name': 'B4/0/1',
    	       'signalling': 'TE',
      	     'spanno': 4,
        	   'type': 'BRI'},
	          {'alarms': ['RED'],
  	         'channels': [74, 76],
    	       'config': {'coding': 'AMI',
        	              'coding_opts': ['B8ZS', 'AMI', 'HDB3'],
          	            'framing': 'CCS',
            	          'framing_crc4': False,
              	        'framing_opts': ['ESF', 'D4', 'CCS', 'CRC4'],
                	      'lbo': 0,
                      'syncsrc': 0},
      	     'description': 'B4XXP (PCI) Card 0 Span 2',
        	   'devicetype': 'Wildcard B410P',
          	 'irq': 18,
	           'manufacturer': 'Digium',
  	         'name': 'B4/0/2',
    	       'signalling': 'TE',
      	     'spanno': 5,
        	   'type': 'BRI'},
	          {'alarms': ['RED'],
  	         'channels': [77, 79],
    	       'config': {'coding': 'AMI',
      	            	  'coding_opts': ['B8ZS', 'AMI', 'HDB3'],
        	        	    'framing': 'CCS',
          	          	'framing_crc4': False,
		           	        'framing_opts': ['ESF', 'D4', 'CCS', 'CRC4'],
  	            	      'lbo': 0,
    	            	    'syncsrc': 0},
  	         'description': 'B4XXP (PCI) Card 0 Span 3',
	           'devicetype': 'Wildcard B410P',
    	       'irq': 18,
      	     'manufacturer': 'Digium',
        	   'name': 'B4/0/3',
          	 'signalling': 'TE',
  	         'spanno': 6,
	           'type': 'BRI'},
		        {'alarms': ['RED'],
	           'channels': [80, 82],
  	         'config': {'coding': 'AMI',
    	                  'coding_opts': ['B8ZS', 'AMI', 'HDB3'],
      	                'framing': 'CCS',
        	              'framing_crc4': False,
          	            'framing_opts': ['ESF', 'D4', 'CCS', 'CRC4'],
            	          'lbo': 0,
              	        'syncsrc': 0},
	           'description': 'B4XXP (PCI) Card 0 Span 4',
  	         'devicetype': 'Wildcard B410P',
    	       'irq': 18,
      	     'manufacturer': 'Digium',
        	   'name': 'B4/0/4',
	           'signalling': 'TE',
  	         'spanno': 7,
    	       'type': 'BRI'}],
					 'WCTDM/0': [{'alarms': ['OK'],
  	          'channels': [63, 71],
    	        'description': 'Wildcard TDM800P Board 1',
              'devicetype': 'Wildcard TDM800P',
              'irq': 19,
              'manufacturer': 'Digium',
              'name': 'WCTDM/0',
              'ports': [[63, 'FXS', False],
                        [64, 'FXS', False],
                        [65, 'FXS', False],
                        [66, 'FXS', False],
                        [67, 'none', False],
                        [68, 'none', False],
                        [69, 'none', False],
                        [70, 'none', False]],
              'spanno': 3,
              'type': 'analog'}]}
		"""
		(resp, data) = self.client.request('GET', '/dahdi_get_spansinfo', {})
		self.assertEqual(resp.status, 200)
		#import pprint; pprint.pprint(cjson.decode(data))

		"""Get DAHDI PCI cards infos. sample:
			{'0000:03:0c.0': {'description': 'Wildcard TE205P (4th Gen)',
           'device': '0205',
           'driver': 'wct4xxp',
           # True if driver is loaded
           'loaded': True,
           'subsystem_device': '0000',
           'subsystem_vendor': '0004',
           'vendor': 'd161'},
			 '0000:03:0d.0': {'description': 'Wildcard TDM800P',
           'device': '0800',
           'driver': 'wctdm24xxp',
           'loaded': True,
           'subsystem_device': '0800',
           'subsystem_vendor': 'd161',
           'vendor': 'd161'}}
		"""
		(resp, data) = self.client.request('GET', '/dahdi_get_cardsinfo', {})
		self.assertEqual(resp.status, 200)
		#import pprint; pprint.pprint(cjson.decode(data))

	def test_02_genconf(self):
		"""Generate dahdi system.conf"""
		#ref: http://www.voip-info.org/wiki/view/system.conf
		conf = {
			'spans': [{
				'spanno' : 1,
				'type'   : 'E1',						# E1/T1/BRI/analog
				'ports'  : [1,31],
				'config' : {
					'timingsrc': 1,						# 0..
					'lbo'      : 0,           # 0-7
					'framing'  : 'ccs',				#E1: ccs, cas; T1: d4, esf
					'coding'   : 'hdb3',			#E1: hdb3    ; T1: ami, b8zs
					'crc4'     : True,				#if coding=hdb3 only
					'yellow'   : False
				},
				'echocanceller': 'mg2'				#mg2, oslec, kb1, sec2, sec, hpec, None
			}, {
				'spanno' : 3,
				'type'   : 'analog',
				'ports'  : [
					#portnum, device, echochanceler
					# devices: fxoks, fxsks, e&m, fxols, fxsls, fxogs, fxlgs, sf
					(63, 'fxoks', 'mg2'),
					(64, 'fxoks', 'mg2'),
					(65, 'fxoks', 'oslec'),
					(66, 'fxoks', None)
				]
			}, {
				'spanno' : 5,
				'type'   : 'BRI',
				'ports'  : [74, 76],
				'config' : {
					'timingsrc': 5,
					'lbo'      : 0,
					'framing'  : 'ccs',
					'coding'   : 'ami',
					'crc4'     : False,
					'termination': True,
					'softntte' : 'te',
				},
				'echocanceller': None
			}],

			'loadzone'   : ['en','fr'],           #us, fr, it, de, uk, jp, it, sp, hu, ...
			'defaultzone': 'fr'
		}

		(resp, data) = self.client.request('POST', '/dahdi_set_config', conf)
		self.assertEqual(resp.status, 200)


if __name__ == '__main__':
	unittest.main()
