# -!- coding: utf8 -*-
from __future__ import with_statement
"""ha module
"""
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Proformatique, Guillaume Bour <gbour@proformatique.com>

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

import os, os.path, re, logging, fcntl, struct, ConfigParser
from datetime import datetime

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW, CMD_R
from xivo_sysconf import helpers


# //DEFINES//
DIR_RW = 3
def IOCTL_RW(type, nr, size):
	return (DIR_RW << 30 | size << 16 | type << 8 | nr)

# ioctl definition
DAHDI_CODE      = 0xDA
DAHDI_MAX_SPANS = 128

#		. Line configuration 
#			. T1 
CONFIG_D4	 	   = (1 << 4)
CONFIG_ESF	   = (1 << 5)
CONFIG_AMI	   = (1 << 6)
CONFIG_B8ZS	   = (1 << 7)
#			. E1
CONFIG_CCS	   = (1 << 8)			# CCS (ISDN) instead of CAS  = (Robbed Bit) 
CONFIG_HDB3	   = (1 << 9)			# HDB3 instead of AMI  = (line coding) 
CONFIG_CRC4	   = (1 << 10)			# CRC4 framing 
CONFIG_NOTOPEN = (1 << 16)
#			. BRI
CONFIG_NTTE	   = (1 << 11)		# To enable NT mode, set this bit to 1, for TE this should be 0 
CONFIG_TERM	   = (1 << 12)	  # To enable Termination resistance set this bit to 1 

# Alarm Condition bits 
ALARM_NONE     = 0	          # No = alarms
ALARM_RECOVER  = (1 << 0)     # Recovering from alarm
ALARM_LOOPBACK = (1 << 1)     # In loopback
ALARM_YELLOW   = (1 << 2)     # Yellow Alarm
ALARM_RED	     = (1 << 3)     # Red Alarm 
ALARM_BLUE     = (1 << 4)     # Blue Alarm 
ALARM_NOTOPEN  = (1 << 5) 	  #
#		Verbose alarm states (upper byte) 
ALARM_LOS      = (1 << 8)     # Loss of Signal
ALARM_LFA      = (1 << 9)     # Loss of Frame Alignment
ALARM_LMFA     = (1 << 10)    # Loss of Multi-Frame Align 

# signaling type
SIG_BROKEN     = (1 << 31)    # The port is broken and/or failed initialization
SIG_FXO		     = (1 << 12)
SIG_FXS		     = (1 << 13)

# struct dahdi_spaninfo. size == 314B
_s = [
	'spanno',
	'name',
	'description',
	'alarms',
	'txlevel',
	'rxlevel',
	'bpvcount',
	'crc4count',
	'ebitcount',
	'fascount',
	'fecount',
	'cvcount',
	'becount',
	'prbs',
	'errsec',
	'irqmisses',
	'syncsrc',
	'numchans',
	'totalchans',
	'totalspans',
	'lbo',
	'lineconfig',
	'lboname',
	'location',
	'manufacturer',
	'devicetype',
	'irq',
	'linecompat',
	'spantype',
]

# struct dahdi_params. size == 136B
_p = [
	'channo',						# Channel number
	'spanno',						# Span itself
	'chanpos',					# Channel number in span
	'sigtype',					# read-only
	'sigcap',						# read-only
	'rxisoffhook',			# read-only
	'rxbits',						# read-only
	'txbits',						# read-only
	'txhooksig',				# read-only
	'rxhooksig'					# read-only
	'curlaw'						# read-only  -- one of DAHDI_LAW_MULAW or DAHDI_LAW_ALAW
	'idlebits'					# read-only  -- What is considered the idle state
	'name'							# Name of channel
	'prewinktime'
	'preflashtime'
	'winktime'
	'flashtime'
	'starttime'
	'rxwinktime'
	'rxflashtime'
	'debouncetime'
	'pulsebreaktime'
	'pulsemaketime'
	'pulseaftertime'
	'chan_alarms'				# alarms on this channel
]

PCI_IDS = {
	# from wct4xxp
	'10ee:0314'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE410P/TE405P (1st Gen)' },
	'd161:1420'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE420 (5th Gen)' },
	'd161:1410'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE410P (5th Gen)' },
	'd161:1405'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE405P (5th Gen)' },
	'd161:0420/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE420 (4th Gen)' },
	'd161:0410/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE410P (4th Gen)' },
	'd161:0405/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE405P (4th Gen)' },
	'd161:0410/0003'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE410P (3rd Gen)' },
	'd161:0405/0003'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE405P (3rd Gen)' },
	'd161:0410'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE410P (2nd Gen)' },
	'd161:0405'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE405P (2nd Gen)' },
	'd161:1220'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE220 (5th Gen)' },
	'd161:1205'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE205P (5th Gen)' },
	'd161:1210'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE210P (5th Gen)' },
	'd161:0220/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE220 (4th Gen)' },
	'd161:0205/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE205P (4th Gen)' },
	'd161:0210/0004'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE210P (4th Gen)' },
	'd161:0205/0003'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE205P (3rd Gen)' },
	'd161:0210/0003'	: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE210P (3rd Gen)' },
	'd161:0205'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE205P ' },
	'd161:0210'		: { 'driver' : 'wct4xxp', 'description' : 'Wildcard TE210P ' },

	# from wctdm24xxp
	'd161:2400'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard TDM2400P' },
	'd161:0800'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard TDM800P' },
	'd161:8002'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard AEX800' },
	'd161:8003'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard AEX2400' },
	'd161:8005'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard TDM410P' },
	'd161:8006'		: { 'driver' : 'wctdm24xxp', 'description' : 'Wildcard AEX410P' },
	'd161:8007'		: { 'driver' : 'wctdm24xxp', 'description' : 'HA8-0000' },
	'd161:8008'		: { 'driver' : 'wctdm24xxp', 'description' : 'HB8-0000' },

	# from pciradio
	'e159:0001/e16b'	: { 'driver' : 'pciradio', 'description' : 'PCIRADIO' },

	# from wcfxo
	'e159:0001/8084'	: { 'driver' : 'wcfxo', 'description' : 'Wildcard X101P clone' },
	'e159:0001/8085'	: { 'driver' : 'wcfxo', 'description' : 'Wildcard X101P' },
	'e159:0001/8086'	: { 'driver' : 'wcfxo', 'description' : 'Wildcard X101P clone' },
	'e159:0001/8087'	: { 'driver' : 'wcfxo', 'description' : 'Wildcard X101P clone' },
	'1057:5608'		: { 'driver' : 'wcfxo', 'description' : 'Wildcard X100P' },

	# from wct1xxp
	'e159:0001/6159'	: { 'driver' : 'wct1xxp', 'description' : 'Digium Wildcard T100P T1/PRI or E100P E1/PRA Board' },

	# from wctdm
	'e159:0001/a159'	: { 'driver' : 'wctdm', 'description' : 'Wildcard S400P Prototype' },
	'e159:0001/e159'	: { 'driver' : 'wctdm', 'description' : 'Wildcard S400P Prototype' },
	'e159:0001/b100'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV E/F' },
	'e159:0001/b1d9'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV I' },
	'e159:0001/b118'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV I' },
	'e159:0001/b119'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV I' },
	'e159:0001/a9fd'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	'e159:0001/a8fd'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	'e159:0001/a800'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	'e159:0001/a801'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	'e159:0001/a908'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	'e159:0001/a901'	: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },
	#'e159:0001'		: { 'driver' : 'wctdm', 'description' : 'Wildcard TDM400P REV H' },

	# from wcte11xp
	'e159:0001/71fe'	: { 'driver' : 'wcte11xp', 'description' : 'Digium Wildcard TE110P T1/E1 Board' },
	'e159:0001/79fe'	: { 'driver' : 'wcte11xp', 'description' : 'Digium Wildcard TE110P T1/E1 Board' },
	'e159:0001/795e'	: { 'driver' : 'wcte11xp', 'description' : 'Digium Wildcard TE110P T1/E1 Board' },
	'e159:0001/79de'	: { 'driver' : 'wcte11xp', 'description' : 'Digium Wildcard TE110P T1/E1 Board' },
	'e159:0001/797e'	: { 'driver' : 'wcte11xp', 'description' : 'Digium Wildcard TE110P T1/E1 Board' },

	# from wcte12xp
	'd161:0120'		: { 'driver' : 'wcte12xp', 'description' : 'Wildcard TE12xP' },
	'd161:8000'		: { 'driver' : 'wcte12xp', 'description' : 'Wildcard TE121' },
	'd161:8001'		: { 'driver' : 'wcte12xp', 'description' : 'Wildcard TE122' },

	# from wcb4xxp
	'd161:b410'		: { 'driver' : 'wcb4xxp', 'description' : 'Digium Wildcard B410P' },

	# from tor2
	'10b5:9030'		: { 'driver' : 'tor2', 'description' : 'PLX 9030' },
	'10b5:3001'		: { 'driver' : 'tor2', 'description' : 'PLX Development Board' },
	'10b5:d00d'		: { 'driver' : 'tor2', 'description' : 'Tormenta 2 Quad T1/PRI or E1/PRA' },
	'10b5:4000'		: { 'driver' : 'tor2', 'description' : 'Tormenta 2 Quad T1/E1 (non-Digium clone)' },

	# # from wctc4xxp
	'd161:3400'		: { 'driver' : 'wctc4xxp', 'description' : 'Wildcard TC400P' },
	'd161:8004'		: { 'driver' : 'wctc4xxp', 'description' : 'Wildcard TCE400P' },

	# Cologne Chips:
	# (Still a partial list)
	'1397:08b4/1397:b540'	: { 'driver' : 'wcb4xxp', 'description' : 'Swyx 4xS0 SX2 QuadBri' },
	'1397:08b4/1397:b556'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns DuoBRI ISDN card' },
	'1397:08b4/1397:b520'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns QuadBRI ISDN card' },
	'1397:08b4/1397:b550'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns QuadBRI ISDN card' },
	'1397:08b4/1397:b752'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns QuadBRI ISDN PCI-E card' },
	'1397:16b8/1397:b552'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns OctoBRI ISDN card' },
	'1397:16b8/1397:b55b'	: { 'driver' : 'wcb4xxp', 'description' : 'Junghanns OctoBRI ISDN card' },
	'1397:08b4/1397:e884'	: { 'driver' : 'wcb4xxp', 'description' : 'OpenVox B200P' },
	'1397:08b4/1397:e888'	: { 'driver' : 'wcb4xxp', 'description' : 'OpenVox B400P' },
	'1397:16b8/1397:e998'	: { 'driver' : 'wcb4xxp', 'description' : 'OpenVox B800P' },
	'1397:08b4/1397:b566'	: { 'driver' : 'wcb4xxp', 'description' : 'BeroNet BN2S0' },
	'1397:08b4/1397:b560'	: { 'driver' : 'wcb4xxp', 'description' : 'BeroNet BN4S0' },
	'1397:08b4/1397:b762'	: { 'driver' : 'wcb4xxp', 'description' : 'BeroNet BN4S0 PCI-E card' },
	'1397:16b8/1397:b562'	: { 'driver' : 'wcb4xxp', 'description' : 'BeroNet BN8S0' },
	'1397:08b4'		: { 'driver' : 'qozap', 'description' : 'Generic Cologne ISDN card' },
	'1397:16b8'		: { 'driver' : 'qozap', 'description' : 'Generic OctoBRI ISDN card' },
	'1397:30b1'		: { 'driver' : 'cwain', 'description' : 'HFC-E1 ISDN E1 card' },
	'1397:2bd0'		: { 'driver' : 'zaphfc', 'description' : 'HFC-S ISDN BRI card' },
	# Has three submodels. Tested with 0675:1704:
	'1043:0675'		: { 'driver' : 'zaphfc', 'description' : 'ASUSTeK Computer Inc. ISDNLink P-IN100-ST-D' },
	'1397:f001'		: { 'driver' : 'ztgsm', 'description' : 'HFC-GSM Cologne Chips GSM' },

	# Rhino cards (based on pci.ids)
	'0b0b:0105'	: { 'driver' : 'r1t1', 'description' : 'Rhino R1T1' },
	'0b0b:0205'	: { 'driver' : 'r4fxo', 'description' : 'Rhino R14FXO' },
	'0b0b:0206'	: { 'driver' : 'rcbfx', 'description' : 'Rhino RCB4FXO 4-channel FXO analog telphony card' },
	'0b0b:0305'	: { 'driver' : 'r1t1', 'description' : 'Rhino R1T1' },
	'0b0b:0405'	: { 'driver' : 'rcbfx', 'description' : 'Rhino R8FXX' },
	'0b0b:0406'	: { 'driver' : 'rcbfx', 'description' : 'Rhino RCB8FXX 8-channel modular analog telphony card' },
	'0b0b:0505'	: { 'driver' : 'rcbfx', 'description' : 'Rhino R24FXX' },
	'0b0b:0506'	: { 'driver' : 'rcbfx', 'description' : 'Rhino RCB24FXS 24-Channel FXS analog telphony card' },
	'0b0b:0605'	: { 'driver' : 'rxt1', 'description' : 'Rhino R2T1' },
	'0b0b:0705'	: { 'driver' : 'rcbfx', 'description' : 'Rhino R24FXS' },
	'0b0b:0706'	: { 'driver' : 'rcbfx', 'description' : 'Rhino RCB24FXO 24-Channel FXO analog telphony card' },
	'0b0b:0906'	: { 'driver' : 'rcbfx', 'description' : 'Rhino RCB24FXX 24-channel modular analog telphony card' },

	# Sangoma cards (based on pci.ids)
	'1923:0040'	: { 'driver' : 'wanpipe', 'description' : 'Sangoma Technologies Corp. A200/Remora FXO/FXS Analog AFT card' },
	'1923:0100'	: { 'driver' : 'wanpipe', 'description' : 'Sangoma Technologies Corp. A104d QUAD T1/E1 AFT card' },
	'1923:0300'	: { 'driver' : 'wanpipe', 'description' : 'Sangoma Technologies Corp. A101 single-port T1/E1' },
	'1923:0400'	: { 'driver' : 'wanpipe', 'description' : 'Sangoma Technologies Corp. A104u Quad T1/E1 AFT' },

	# Yeastar (from output of modinfo):
	'e159:0001/2151' : { 'driver' : 'ystdm8xx', 'description' : 'Yeastar YSTDM8xx'},

	'e159:0001/9500:0003' : { 'driver' : 'opvxa1200', 'description' : 'OpenVox A800P' },

	# Aligera
 	'10ee:1004'		: { 'driver' : 'ap400', 'description' : 'Aligera AP40X/APE40X 1E1/2E1/4E1 card' },

	# XiVO IPBX OpenHardware (WARNING: Any device on the Tolapai's LEB/SSP
	# controllers will be detected, including subsequent revisions)
	'8086:503d'	: { 'driver' => 'xivoxhfc', 'description' => 'XiVO IPBX OpenHardware,	ISDN BRI interfaces (Cologne XHFC-4SU)' },
	'8086:503b'	=> { 'driver' => 'xivovp', 'description' => 'XiVO IPBX OpenHardware, FXO/FXS interfaces (Zarlink Ve890)' },
}

# //END-DEFINES//


class Dahdi(object):
	"""
	"""
	def __init__(self):
		super(Dahdi, self).__init__()
		self.log = logging.getLogger('xivo_sysconf.modules.dahdi')

		http_json_server.register(self.spansinfo , CMD_R,	name='dahdi_get_spansinfo',
			safe_init=self.safe_init)
		http_json_server.register(self.cardsinfo , CMD_R,	name='dahdi_get_cardsinfo')
		http_json_server.register(self.setconfig , CMD_RW,	name='dahdi_set_config')

	def safe_init(self, options):
		self.systemconf = options.configuration.get('dahdi', 'systemconf_file')
		self.tmpl       = options.configuration.get('dahdi', 'userconf_file')

	def spansinfo(self, args, options):
		"""Basically a reimplementation of dahdi_scan program
		"""
		try:
			fd = open('/dev/dahdi/ctl', 'r')
		except:
			raise HttpReqError(500, "cannot open dahdi ioctl pseudo-file")

		basechan = 1
		spans		 = {}
		# foreach -maybe- span
		for spanno in xrange(1,DAHDI_MAX_SPANS):
			pack = struct.pack('i310s',spanno,'')

			try:
				ret = fcntl.ioctl(fd, IOCTL_RW(DAHDI_CODE, 10, 314), pack)
			except IOError:
				# no span found
				continue

			ret       = struct.unpack('i20s40s19i40s40s40s40s2i6s', ret)

			# get span info
			span = {
				'spanno'  : spanno, 
				'irq'     : ret[_s.index('irq')],
				'channels': (basechan, basechan+ret[_s.index('totalchans')]),
				'alarms'  : [],
			}
			for k in ('name','description','manufacturer','devicetype'):
				span[k] = ret[_s.index(k)].split('\x00')[0]

			# alarms
			alarms = ret[_s.index('alarms')]
			if alarms != 0:
				for alarm in ('BLUE','YELLOW','RED','LOOPBACK','RECOVER','NOTOPEN'):
					if alarms & eval('ALARM_'+alarm) != 0:
						span['alarms'].append(alarm)

				if 'RED' in span['alarms'] and alarms & ALARM_LFA:
					span['alarms'].append('LFA')
			elif ret[_s.index('numchans')] != 0:
				#TODO: complete
				span['alarms'].append('OK')
			else:
				span['alarms'].append('UNCONFIGURED')

			# span settings
			isdigital = ret[_s.index('linecompat')] > 0
			if isdigital:
				span['type'] = ret[_s.index('spantype')].split('\x00')[0]

				span['config'] = {
					'syncsrc'     : ret[_s.index('syncsrc')],
					'lbo'         : ret[_s.index('lbo')],
					'coding_opts' : [],
					'framing_opts': [],
					'coding'      : None,
					'framing'     : None,
					'framing_crc4': ret[_s.index('lineconfig')] & CONFIG_CRC4 != 0,
				}
				# coding_opts
				for c in ('B8ZS','AMI','HDB3'):
					if ret[_s.index('linecompat')] & eval('CONFIG_'+c) != 0:
						span['config']['coding_opts'].append(c)
				# framing_opts
				for c in ('ESF','D4','CCS','CRC4'):
					if ret[_s.index('linecompat')] & eval('CONFIG_'+c) != 0:
						span['config']['framing_opts'].append(c)
				# coding
				for c in ('B8ZS','AMI','HDB3'):
					if ret[_s.index('lineconfig')] & eval('CONFIG_'+c) != 0:
						span['config']['coding'] = c; break
				# framing
				for c in ('ESF','D4','CCS'):
					if ret[_s.index('lineconfig')] & eval('CONFIG_'+c) != 0:
						span['config']['framing'] = c; break
	
			else:
				# analogic
				span['type']  = 'analog'
				span['ports'] = [None for x in range(ret[_s.index('totalchans')])]

				# for each channel
				for channo in xrange(basechan, basechan+ret[_s.index('totalchans')]):
					pack = struct.pack('i132s', channo,'')
					try:
						chan = fcntl.ioctl(fd, IOCTL_RW(DAHDI_CODE, 5, 136), pack)
					except IOError:
						continue
					chan = struct.unpack('12i40s12i', chan)

					sig = 'none'
					if chan[_p.index('sigcap')] & SIG_FXO != 0:
						sig = 'FXS'
					elif chan[_p.index('sigcap')] & SIG_FXS != 0:
						sig = 'FXO'

					span['ports'][channo-basechan] = (channo, sig, chan[_p.index('sigcap')] & SIG_BROKEN	!= 0)

			spangroup = '/'.join(ret[_s.index('name')].split('\x00')[0].split('/')[:2])
			spans.setdefault(spangroup, []).append(span)

			basechan += ret[_s.index('totalchans')]

		return spans

	def cardsinfo(self, args, options):
		"""Basically a -incomplete- reimplementation of dahdi_hardware program
		"""
		devices = {}
		DEVPATH = '/sys/bus/pci/devices'

		for pciid in os.listdir(DEVPATH):
			dev = {'loaded': False}
			for k in ('vendor','device','subsystem_vendor','subsystem_device'):
				with open(os.path.join(DEVPATH,pciid,k)) as f:
					dev[k] = f.read()[2:-1] # remove starting '0x' and trailing '\n'

			pcikey = re.split('([:/])',
				"{vendor}:{device}/{subsystem_vendor}:{subsystem_device}".format(**dev))
			for i in (7,5,3):
				subkey = ''.join(pcikey[:i])
				if subkey in PCI_IDS:
					dev.update(PCI_IDS[subkey]); devices[pciid] = dev; break


		DRVPATH = '/sys/bus/pci/drivers'
		for drvname in os.listdir(DRVPATH):
			try:
				# fail if no pciid (i.e 0000:03:0c.0) found
				pciid = [f for f in os.listdir(os.path.join(DRVPATH, drvname)) if	re.match("^[\da-f.:]+$", f)][0]

				# fail if no module defined for pci device
				modname = os.path.basename(os.readlink(os.path.join(DRVPATH, drvname, 'module')))

				# fail if pci device is unknown
				devices[pciid]['loaded'] = devices[pciid]['driver'] == modname
			except:
				continue
		
		return devices

	def _loadtmpl(self, filename):
		if not os.path.exists(filename):
			return {}

		tmpl    = {}
		section = None
		with open(filename, 'r') as f:
			for l in f.xreadlines():
				h = l.strip()
				if len(h) > 0 and h[0] == '#': # comment
					continue

				elif len(h) > 0 and h[0] == '[':
					section = h[1:-1]; tmpl[section] = ''

				elif section is not None:
					tmpl[section] += l

		return tmpl

	def setconfig(self, args, options):
		usertmpl = self._loadtmpl(self.tmpl)

		# which port is dchan depend on ISDN mode
		DIGITAL_DCHAN = {
			'E1' : 15,
			'T1' : 23,
			'BRI': 2
		}

		with open(self.systemconf, 'w') as f:
			print >>f, "### AUTOMATICALLY GENERATED BY sysconfd. DO NOT EDIT ###"
			print >>f, datetime.now().strftime("# $%Y/%m/%d %H:%M:%S$")

			for span in args.get('spans',[]):
				if str(span['spanno']) in usertmpl:
					continue

				print >>f, "\n# span #%d (%s)" % (span['spanno'],span['type'])

				if span['type'] == 'analog':
					for port in span['ports']:
						print >>f, "%s=%d" % (port[1], port[0])
						if port[2] is not None:
							print >>f, "echocanceller=%s,%d" % (port[2], port[0])
				else:
					c = span['config']
					print >>f, "span=%d,%d,%d,%s,%s%s%s" % (
						span['spanno'],	c['timingsrc'],	c['lbo'], c['framing'],	c['coding'],
						',crc4'   if c.get('crc4',False) else '',
						',yellow' if c.get('yellow',False) else ''
					)

					dchan = DIGITAL_DCHAN[span['type'].upper()]
					bchan = "%s%s%s" % (
						"%d-%d" % (span['ports'][0], span['ports'][0]+dchan-1) if dchan != span['ports'][0] else '',
						',' if (span['ports'][0]+dchan) not in span['ports'] else '',
						"%d-%d" % (span['ports'][0]+dchan+1, span['ports'][1]) if	span['ports'][0]+dchan != span['ports'][1] else ''
					)

					print >>f, "bchan=%s" % bchan
					print >>f, "%s=%d" % ('hardhdlc' if span['type'] == 'BRI' else 'dchan', span['ports'][0]+dchan,)

					if span.get('echocanceller',False):
						print >>f, "echocanceller=%s,%s" % (span.get('echocanceller',False), bchan)

			for name, content in usertmpl.iteritems():
				if name == 'global':
					continue
				print >>f, "\n# span #%s (HAND-EDITED STATIC CONF)" % name
				print >>f, content.strip()

			print >>f, "\n# global data"
			if 'global' in usertmpl:
				print >>f, "# HAND EDITED STATIC CONF"
				print >>f, usertmpl['global'].strip()
			else:
				if 'loadzone' in args:
					for z in args['loadzone']:
						print >>f, "loadzone=%s" % z

				if 'defaultzone' in args:
					print >>f, "defaultzone=%s" % args['defaultzone']

dahdi = Dahdi()

