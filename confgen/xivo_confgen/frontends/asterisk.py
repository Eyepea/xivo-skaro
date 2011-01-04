# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010  Proformatique, Guillaume Bour <gbour@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""
from cStringIO import StringIO
from frontend  import Frontend

class AsteriskFrontend(Frontend):
	def sip_conf(self):
		"""

			o - output stream. write to it with *print >>o, 'blablabla'*
		"""
		o = StringIO()
		
		## section::general
		print >>o, '[general]'
		for item in self.backend.sip.all(commented=False):
			if item['var_name'] in ('register', 'mwi'):
				print >>o, item['var_name'], "=>", item['var_val']

			elif item['var_name'] not in ['allow', 'disallow']:
				print >>o, item['var_name'], "=", item['var_val']

			elif item['var_name'] == 'allow':
				print >>o, 'disallow = all'
				for c in item['var_val'].split(','):
					print >>o, 'allow = %s' % c

		## section::authentication
		items = self.backend.sipauth.all()
		if len(items) > 0:
			print >>o, '\n[authentication]'

			for auth in items:
				mode = '#' if auth['secretmode'] == 'md5' else ':'
				print >>o, "auth = %s%s%s@%s" % (auth['user'], mode, auth['secret'], auth['realm'])


		# section::trunks
		for trunk in self.backend.siptrunks.all(commented=False):
			print >>o, "\n[%s]" % trunk['name']

			for k, v in trunk.iteritems():
				if k in ('id','name','protocol','category','commented','disallow') or v in (None, ''):
					continue

				if isinstance(v, unicode):
					v = v.encode('utf8')

				if v == 'allow':
					print >>o, "disallow = all"
					for c in v.split(','):
						print >>o, "allow = " + str(c)
				else:
					print >>o, k, '=', v


		# section::users
		for user in self.backend.sipusers.all(commented=False):
			print >>o, "\n[%s]" % user['name']

			for k, v in user.iteritems():
				if k in ('id','name','protocol','category','commented','initialized','disallow') or\
					 v in (None, ''):
					continue

				if k not in ('regseconds','lastms','name','fullcontact','ipaddr','allow','disallow','subscribemwi'):
					if isinstance(v, unicode):
						v = v.encode('utf8')
					print >>o, k + " = " + str(v)

				if k == 'allow' and v != None:
					print >>o, "disallow = all"
					for c in v.split(','):
						print >>o, "allow = " + str(c)

				if k == 'subscribemwi' and v is not None:
					v = 'no' if v == '0' else 'yes'
					print >>o, "subscribemwi = " + str(v)


		return o.getvalue()


	def iax_conf(self):
		o = StringIO()
		
		## section::general
		print >>o, '[general]'
		for item in self.backend.iax.all(commented=False):
			if item['var_name'] == 'register':
				print >>o, item['var_name'], "=>", item['var_val']

			elif item['var_name'] not in ['allow', 'disallow']:
				print >>o, "%s = %s" % (item['var_name'], item['var_val'])

			elif item['var_name'] == 'allow':
				print >>o, 'disallow = all'
				for c in item['var_val'].split(','):
					print >>o, 'allow = %s' % c


		## section::authentication
		items = self.backend.iaxcalllimits.all()
		if len(items) > 0:
			print >>o, '\n[callnumberlimits]'

			for item in items:
				print >>o, "%s/%s = %s" % (item['destination'], item['netmask'], item['calllimits'])


		# section::trunks
		for trunk in self.backend.iaxtrunks.all(commented=False):
			print >>o, "\n[%s]" % trunk['name']

			for k, v in trunk.iteritems():
				if k in ('id','name','protocol','category','commented','disallow') or v in (None, ''):
					continue

				if isinstance(v, unicode):
					v = v.encode('utf8')

				if k == 'allow' and v != None:
					print >>o, "disallow = all"
					for c in v.split(','):
						print >>o, "allow = " + str(c)
				else:
					print >>o, k + " = ", v

		# section::users
		for user in self.backend.iaxusers.all(commented=False):
			print >>o, "\n[%s]" % user['name']

			for k, v in user.iteritems():
				if k in ('id','name','protocol','category','commented','initialized','disallow') or\
					 v in (None, ''):
					continue

				if isinstance(v, unicode):
					v = v.encode('utf8')

				if k == 'allow' and v != None:
					print >>o, "disallow = all"
					for c in v.split(','):
						print >>o, "allow = " + str(c)
				else:
					print >>o, k, "=", str(v)


		return o.getvalue()


	def sccp_conf(self):
		o = StringIO()
		
		## section::general
		print >>o, '[general]'
		for item in self.backend.sccp.all(commented=False):
			#print item, type(item)
			if item['var_name'] not in ['allow', 'disallow']:
				print >>o, item['var_name'], "=", item['var_val']

			elif item['var_name'] == 'allow':
				print >>o, 'disallow = all'
				for c in item['var_val'].split(','):
					print >>o, 'allow = %s' % c


		# section::users (phones)
		from xivo import xivo_config
		from xivo import all_phones
		from xivo.provisioning import get_funckeys

		for user in self.backend.sccpusers.all(commented=False):
			#print user.keys()
			name = 'SEP' + user['macaddr'].replace(':', '')
			phone_class = xivo_config.phone_factory({'vendor': user['vendor'], 'model': user['model']})
			if not phone_class:
				continue

			addons = []
			if user['addons'] and len(user['addons']) > 0:
				addons = user['addons'].split(',')
				devicetype = addons[0]
			else:
				devicetype = phone_class.get_sccp_devicetype(user['model'])
				if not devicetype:
					continue

			print >>o, "\n[%s]" % name
			print >>o, "type = device"
			print >>o, "devicetype = %s" % devicetype
			for addon in addons:
				print >>o, "addon = %s" % addon

			softkeys = {}
			for k, v in user.items():
				#print k, v
				#k = k.split('.')[1]
				if k in ['id', 'name', 'macaddr', 'vendor', 'model','defaultline', 'addons', 'number', 'commented', 'featid', 'protocol'] \
					 or v is None or len(str(v)) == 0:
					continue

				if k.startswith('softkey_'):
					softkeys[k[8:]] = v
					continue

				print >>o, "%s = %s" % (k, v)

			dftline = self.backend.sccpusers.default_line(user['defaultline'])
			if dftline is not None:
				print >>o, "button = line, %s" % dftline['name']

			# map buttons
			""" SKIPPED FROM NOW AS WE DONT USE xivo libpython SQL Cursor
			fknum = 2
			funckeys = get_funckeys(cursor, user['featid'], user['number'])
			ids = funckeys.keys()
			ids.sort()
    
			for num in ids:
				# button #1 is reserved for phone default line
				if num == 1:
					continue

				# fill empty buttons
				for i in xrange(fknum, num):
					print "button = empty"
				fknum = num

				btn = funckeys[num]
				label = btn['label']
				if label is None:
					label = btn.get('altlabel')

				print "button = speeddial, %s, %s," % (label, btn['exten']),
				if btn['supervision']:
					print "%s@%s" % (btn['exten'], btn['context'])
				else:
					print

				fknum += 1
			"""

			# soft keys
			if len(softkeys) > 0:
				print >>o, "softkeyset = keyset_%s" % name

 				## END OF DEVICE / START OF SOFTKEY
				print >>o, "\n[keyset_%s]" % name
				print >>o, "type = softkeyset"
        
				for k, v in softkeys.iteritems():
					print >>o, "%s = %s" % (k, v)


		# section::lines
		for l in self.backend.sccplines.all(commented=False):
			print >>o, "\n[%s]" % l['name']
   
			label = l['label']
			if not label or len(label) == 0:
				label = l['name']

			print >>o, "type = line"
			print >>o, "id = %s" % l['name']
			print >>o, "label = %s" % label
			print >>o, "pin = %s" % l['pin']
			print >>o, "cid_name = %s" % l['cid_name']
			print >>o, "cid_num = %s" % l['cid_num']

			for k, v in l.iteritems():
				if k in ('id','name','label','cid_name','cid_num','commented') or v in (None, ''):
					continue

				if isinstance(v, unicode):
					v = v.encode('utf8')
				print >>o, k + " = " + str(v)

		return o.getvalue()


	def voicemail_conf(self):
		o = StringIO()

		## section::general
		print >>o, '[general]'
		for item in self.backend.voicemail.all(commented=False, category='general'):
			if item['var_name'] == 'emailbody':
				item['var_val'] = item['var_val'].replace('\n', '\\n')
			print >>o, "%s = %s" % (item['var_name'], item['var_val'])

		print >>o, '\n[zonemessages]'
		for item in self.backend.voicemail.all(commented=False, category='zonemessages'):
			print >>o, "%s = %s" % (item['var_name'], item['var_val'])


		context  = None
		excluded = ('uniqueid','context','mailbox','password','fullname','email','pager','commented','imapuser','imappassword','imapfolder')
		imapusers = []

		for vm in self.backend.voicemails.all(commented=False, order='context'):
			if vm['context'] != context:
				print >>o, '\n[%s]' % vm['context']; context = vm['context']

			print >>o, "%s => %s,%s,%s,%s,%s" % (
				vm['mailbox'],
				vm['password'],
				'' if vm['fullname'] is None else vm['fullname'],
				'' if vm['email'] is None else vm['email'],
				'' if vm['pager'] is None else vm['pager'],
				'|'.join(["%s=%s" % (k, vm[k]) for k in vm.iterkeys() if k not in excluded and vm[k] is not None])
			)

			if vm['imapuser'] is not None:
				imapusers.append(vm)

		if len(imapusers) > 0:
			print >>o, '\n[imapvm]'

			for vm in imapusers:
				print >>o, "%s => %s,%s,%s,%s,%s" % (
					vm['mailbox'],
					vm['password'],
					'' if vm['fullname'] is None else vm['fullname'],
					'' if vm['email'] is None else vm['email'],
					'' if vm['pager'] is None else vm['pager'],
					'|'.join(["%s=%s" % (k, vm[k]) for k in vm.iterkeys() if k in ('imapuser','imappassword','imapfolder') and vm[k] is not None])
				)


		return o.getvalue()


	def queues_conf(self):
		o = StringIO()

		print >>o, '\n[general]'
		for item in self.backend.queue.all(commented=False, category='general'):
			print >>o, "%s = %s" % (item['var_name'], item['var_val'])


		for q in self.backend.queues.all(commented=False, order='name'):
			print >>o, '\n[%s]' % q['name']

			for k, v in q.iteritems():
				if k in ('name','category','commented') or v is None or \
						(isinstance(v, (str,unicode)) and len(v) == 0):
					continue

				print >>o, k,'=',v

			for m in self.backend.queuemembers.all(commented=False, queue_name=q['name']):
				o.write("member => %s" % m['interface'])
				if m['penalty'] > 0:
					o.write(",%d" % m['penalty'])
				o.write('\n')

		return o.getvalue()

	def agents_conf(self):
		o = StringIO()

		print >>o, '\n[general]'
		for c in self.backend.agent.all(commented=False, category='general'):
			print >>o, "%s = %s" % (c['var_name'], c['var_val'])
		
		print >>o, '\n[agents]'
		for c in self.backend.agent.all(commented=False, category='agents'):
			if c['var_val'] is None or c['var_name'] == 'agent':
				continue

			print >>o, "%s = %s" % (c['var_name'], c['var_val'])

		print >>o, ''
		for a in self.backend.agentusers.all(commented=False):
			for k, v in a.items():
				if k == 'var_val':
					continue

				print >>o, "%s = %s" % (k, v)

			print >>o, "agent =>", a['var_val'], "\n"
		
		return o.getvalue()

			
	def meetme_conf(self):
		o = StringIO()

		print >>o, '\n[general]'
		for c in self.backend.meetme.all(commented=False, category='general'):
			print >>o, "%s = %s" % (c['var_name'], c['var_val'])

		print >>o, '\n[rooms]'
		#TODO: list meetmes
			
		return o.getvalue()

	def musiconhold_conf(self):
		o = StringIO()

		cat = None
		for m in self.backend.musiconhold.all(commented=False, order='category'):
			if m['var_val'] is None:
				continue

			if m['category'] != cat:
				cat = m['category']; print >>o, '\n[%s]' % cat

			print >>o, "%s = %s" % (m['var_name'], m['var_val'])

		return o.getvalue()

	def features_conf(self):
		o = StringIO()

		print >>o, '\n[general]'
		for f in self.backend.features.all(commented=False, category='general'):
			print >>o, "%s = %s" % (f['var_name'], f['var_val'])

		print >>o, '\n[featuremap]'
		for f in self.backend.features.all(commented=False, category='featuremap'):
			print >>o, "%s = %s" % (f['var_name'], f['var_val'])

		return o.getvalue()
	
