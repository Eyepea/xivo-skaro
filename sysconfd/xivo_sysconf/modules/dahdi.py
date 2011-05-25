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

import os, os.path, logging, fcntl, struct
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

# //END-DEFINES//


class Dahdi(object):
	"""
	"""
	def __init__(self):
		super(Dahdi, self).__init__()
		self.log = logging.getLogger('xivo_sysconf.modules.dahdi')

		http_json_server.register(self.dahdi_get_spaninfos , CMD_R, name='dahdi_get_spaninfos',
			safe_init=self.safe_init)
		#http_json_server.register(self.status   , CMD_R , name='ha_status')

	def safe_init(self, options):
		#self.file       = options.configuration.get('ha', 'ha_file')
		pass

	def dahdi_get_spaninfos(self, args, options):
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

dahdi = Dahdi()

