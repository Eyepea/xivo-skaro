# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

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
import re
from xivo             import OrderedConf
from xivo             import xivo_helpers

from cStringIO        import StringIO
from confgen.frontend import Frontend


class AsteriskFrontend(Frontend):
    def sip_conf(self):
        """

            o - output stream. write to it with *print >>o, 'blablabla'*
        """
        o = StringIO()
        
        ## section::general
        print >>o, '[general]'
        for item in self.backend.sip.all(commented=False):
            if item['var_val'] is None:
                continue

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


        # section::users (xivo lines)
        pickups = {}
        for p in self.backend.pickups.all(usertype='sip'):
            user = pickups.setdefault(p[0], {})
            user.setdefault(p[1], []).append(str(p[2]))

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

            if user['name'] in pickups:
                p = pickups[user['name']]
                #WARNING: 
                # pickupgroup: trappable calls  (xivo members)
                # callgroup  : can pickup calls (xivo pickups)
                if 'member' in p:
                    print >>o, "pickupgroup = " + ','.join(frozenset(p['member']))
                if 'pickup' in p:
                    print >>o, "callgroup = " + ','.join(frozenset(p['pickup']))


        return o.getvalue()


    def iax_conf(self):
        o = StringIO()
        
        ## section::general
        print >>o, '[general]'
        for item in self.backend.iax.all(commented=False):
            if item['var_val'] is None:
                continue

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

            for auth in items:
                print >>o, "%s/%s = %s" % (auth['destination'], auth['netmask'], auth['calllimits'])


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
            print >>o, item['var_name'], '=', item['var_val'].encode('utf8')

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


        penalties = dict([(itm['id'], itm['name']) for itm in    self.backend.queuepenalty.all(commented=False)])

        print >>o, '\n[general]'
        for item in self.backend.queue.all(commented=False, category='general'):
            print >>o, "%s = %s" % (item['var_name'], item['var_val'])


        for q in self.backend.queues.all(commented=False, order='name'):
            print >>o, '\n[%s]' % q['name']

            for k, v in q.iteritems():
                if k in ('name','category','commented') or v is None or \
                        (isinstance(v, (str,unicode)) and len(v) == 0):
                    continue

                if k == 'defaultrule':
                    if not int(v) in penalties:
                        continue
                    v = penalties[int(v)]

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

        # parkinglots
        for f in self.backend.parkinglot.all(commented=False):
            print >>o, "\n[parkinglot_%s]" % f['name']
            print >>o, "context => %s" % f['context']
            print >>o, "parkext => %s" % f['extension']
            print >>o, "parkpos => %d-%d" % (int(f['extension'])+1, int(f['extension'])+f['positions'])
            if f['next'] == 1:
                print >>o, "findslot => next"

            mmap = {
                'duration'     : 'parkingtime',
                'calltransfers': 'parkedcalltransfers',
                'callreparking': 'parkedcallreparking',
                'callhangup'   : 'parkedcallhangup',
                'callreparking': 'parkedcallreparking',
                'musicclass'   : 'parkedmusicclass',
                'hints'        : 'parkinghints',
            }
            for k, v in mmap.iteritems():
                if f[k] is not None:
                    print >>o, "%s => %s" % (v, str(f[k]))
                
        print >>o, '\n[featuremap]'
        for f in self.backend.features.all(commented=False, category='featuremap'):
            print >>o, "%s = %s" % (f['var_name'], f['var_val'])

        return o.getvalue()


    def queueskills_conf(self):
        """Generate queueskills.conf asterisk configuration file
        """
        o = StringIO()

        userid = None
        for sk in self.backend.userqueueskills.all():
            if userid != sk['id']:
                print >>o, "\n[user-%d]" % sk['id']
                userid = sk['id']

            print >>o, "%s = %s" % (sk['name'], sk['weight'])

        agentid = None
        for sk in self.backend.agentqueueskills.all():
            if agentid != sk['id']:
                print >>o, "\n[agent-%d]" % sk['id']
                agentid = sk['id']

            print >>o, "%s = %s" % (sk['name'], sk['weight'])

        return o.getvalue()


    def queueskillrules_conf(self):
        """Generate queueskillrules.conf asterisk configuration file
        """
        o = StringIO()

        for r in self.backend.queueskillrules.all():
            print >>o, "\n[%s]" % r['name']

            if 'rule' in r and r['rule'] is not None:
                for rule in r['rule'].split(';'):
                    print >>o, "rule = %s" % rule

        return o.getvalue()
    

    def extensions_conf(self):
        """Generate extensions.conf asterisk configuration file
        """
        o = StringIO()
        conf    = None

        # load context templates
        if hasattr(self, 'contextsconf'):
            conf = OrderedConf.OrderedRawConf(filename=self.contextsconf)
            if conf.has_conflicting_section_names():
                raise ValueError, self.contextsconf + " has conflicting section names"
            if not conf.has_section('template'):
                raise ValueError, "Template section doesn't exist"

        # hints & features (init)
        xfeatures = {
            'bsfilter':            {},
            'callgroup':           {},
            'callmeetme':          {},
            'callqueue':           {},
            'calluser':            {},
            'fwdbusy':             {},
            'fwdrna':              {},
            'fwdunc':              {},
            'phoneprogfunckey':    {},
            'vmusermsg':           {}}

        extenumbers = self.backend.extenumbers.all(features=xfeatures.keys())
        xfeatures.update(dict([x['typeval'], {'exten': x['exten'], 'commented': x['commented']}] for x in extenumbers))

        # voicemenus
        for vm in self.backend.voicemenus.all(commented=0, order='name'):
            print >>o, "[voicemenu-%s]" % vm['name']

            for act in self.backend.extensions.all(context='voicemenu-'+vm['name'],    commented=0):
                print >>o, "exten = %s,%s,%s(%s)" % \
                        (act['exten'], act['priority'],    act['app'], act['appdata'].replace('|',','))

        # foreach active context
        for ctx in self.backend.contexts.all(commented=False, order='name', asc=False):
            # context name preceded with '!' is ignored
            if conf.has_section('!' + ctx['name']):
                continue

            print >>o, "\n[%s]" % ctx['name']
            # context includes
            for row in self.backend.contextincludes.all(context=ctx['name'], order='priority'):
                print >>o, "include = %s" % row['include']

            if conf.has_section(ctx['name']):
                section = ctx['context']
            elif conf.has_section('type:%s' % ctx['contexttype']):
                section = 'type:%s' % ctx['contexttype']
            else:
                section = 'template'
            
            tmpl = []
            for option in conf.iter_options(section):
                if option.get_name() == 'objtpl':
                    tmpl.append(option.get_value()); continue

                print >>o, "%s = %s" % (option.get_name(), option.get_value().replace('%%CONTEXT%%', ctx['name']))
            print >>o

            # test if we are in DUNDi active/active mode
            dundi_aa = self.backend.general.get(id=1)['dundi'] == 1

            # objects extensions (user, group, ...)
            for exten in self.backend.extensions.all(context=ctx['name'], commented=False, order='context'):
                app     = exten['app']
                appdata = list(exten['appdata'].replace('|',',').split(','))

                # active/active mode
                if dundi_aa and appdata[0] == 'user':
                    exten['priority'] += 1

                if app == 'Macro':
                    app     = 'Gosub'
                    appdata = (appdata[0], 's', '1(' + ','.join(appdata[1:]) + ')')
                
                exten['action'] = "%s(%s)" % (app, ','.join(appdata))

                for line in tmpl:
                    prefix = 'exten =' if line.startswith('%%EXTEN%%') else 'same  =    '

                    def varset(m):
                        return str(exten.get(m.group(1).lower(), ''))
                    line = re.sub('%%([^%]+)%%', varset, line)
                    print >>o, prefix, line
                print >>o

            # phone (user) hints
            hints = self.backend.hints.all(context=ctx['name'])
            if len(hints) > 0:
                print >>o, "; phones hints"

            for hint in hints:
                xid       = hint['id']
                number    = hint['number']
                name      = hint['name']
                proto     = hint['protocol'].upper()
                if proto == 'IAX':
                    proto = 'IAX2'

                if number:
                    print >>o, "exten = %s,hint,%s/%s" % (number, proto, name)

                if not xfeatures['calluser'].get('commented', 1):
                    #TODO: fkey_extension need to be reviewed (see hexanol)
                    print >>o, "exten = %s,hint,%s/%s" % (xivo_helpers.fkey_extension(
                        xfeatures['calluser']['exten'],    (xid,)),
                        proto, name)

                if not xfeatures['vmusermsg'].get('commented', 1) and int(hint['enablevoicemail']) \
                     and hint['uniqueid']:
                    print >>o, "exten = %s%s,hint,%s/%s" % (xfeatures['vmusermsg']['exten'], number, proto, name)


            # objects(user,group,...) supervision
            phonesfk = self.backend.phonefunckeys.all(context=ctx['name'])
            if len(phonesfk) > 0:
                print >>o, "\n; phones supervision"

            xset = set()
            for pkey in phonesfk:
                xtype       = pkey['typeextenumbersright']
                calltype    = "call%s" % xtype

                if pkey['exten'] is not None:
                    exten = xivo_helpers.clean_extension(pkey['exten'])
                elif xfeatures.has_key(calltype) and not xfeatures[calltype].get('commented', 1):
                    exten = xivo_helpers.fkey_extension(
                        xfeatures[calltype]['exten'],
                        (pkey['typevalextenumbersright'],))
                else:
                    continue

                xset.add((exten, ("MeetMe:%s" if xtype == 'meetme' else "Custom:%s") % exten))

            for hint in xset:
                print >>o, "exten = %s,hint,%s" % hint


            # BS filters supervision 
            bsfilters = self.backend.bsfilterhints.all(context=ctx['name'])

            extens    =    set(xivo_helpers.speed_dial_key_extension(xfeatures['bsfilter'].get('exten'),
                r['exten'], None, r['number'], True) for r in bsfilters)

            if len(extens) > 0:
                print >>o, "\n; BS filters supervision"
            for exten in extens:
                print >>o, "exten = %s,hint,Custom:%s" % (exten, exten)


            # prog funckeys supervision
            progfunckeys = self.backend.progfunckeys.all(context=ctx['name'])

            extens = set()
            for k in progfunckeys:
                exten = k['exten']

                if exten is None and k['typevalextenumbersright'] is not None:
                    exten = "*%s" % k['typevalextenumbersright']

                extens.add(xivo_helpers.fkey_extension(xfeatures['phoneprogfunckey'].get('exten'),
                    (k['iduserfeatures'], k['leftexten'], exten)))

            if len(extens) > 0:
                print >>o, "\n; prog funckeys supervision"
            for exten in extens:
                print >>o, "exten = %s,hint,Custom:%s" % (exten, exten)

            # -- end per-context --

        # XiVO features
        context   = 'xivo-features'
        cfeatures = []
        tmpl      = []

        print >>o, "\n[xivo-features]"
        for option in conf.iter_options(context):
            if option.get_name() == 'objtpl':
                tmpl.append(option.get_value()); continue

            print >>o, "%s = %s" % (option.get_name(), option.get_value().replace('%%CONTEXT%%', context))
            print >>o

        for exten in self.backend.extensions.all(context='xivo-features',    commented=0):
            app     = exten['app']
            appdata = list(exten['appdata'].replace('|',',').split(','))
            if app == 'Macro':
                app     = 'Gosub'
                appdata = (appdata[0], 's', '1(' + ','.join(appdata[1:]) + ')')
                
            exten['action'] = "%s(%s)" % (app, ','.join(appdata))

            for line in tmpl:
                prefix = 'exten =' if line.startswith('%%EXTEN%%') else 'same  =    '

                def varset(m):
                    return str(exten.get(m.group(1).lower(), ''))
                line = re.sub('%%([^%]+)%%', varset, line)
                print >>o, prefix, line
            print >>o

        if not xfeatures['vmusermsg'].get('commented', 1):
            vmusermsgexten = xfeatures['vmusermsg']['exten']

            for line in (
                    "1,AGI(agi://${XIVO_AGID_IP}/user_get_vmbox,${EXTEN:%d})" % len(vmusermsgexten),
                    "n,Gosub(xivo-pickup,0,1)",
                    "n,VoiceMailMain(${XIVO_MAILBOX}@${XIVO_MAILBOX_CONTEXT},${XIVO_VMMAIN_OPTIONS})",
                    "n,Hangup()\n"):
                cfeatures.append("_%s%s,%s" % (vmusermsgexten, 'X' * len(vmusermsgexten), line))

        for x in ('busy', 'rna', 'unc'):
            fwdtype = "fwd%s" % x
            if not xfeatures[fwdtype].get('commented', 1):
                cfeatures.append("%s,1,Macro(feature_forward,%s,)"
                    % (xivo_helpers.clean_extension(xfeatures[fwdtype]['exten']), x))

        if cfeatures:
            print >>o, "exten = " + "\nexten = ".join(cfeatures)

        return o.getvalue()

    
    def queuerules_conf(self):
        o = StringIO()

        rule = None
        for m in self.backend.queuepenalties.all():
            if m['name'] != rule:
                rule = m['name']; print >>o, "\n[%s]" % rule

            print >>o, "penaltychange => %d," % m['seconds'],
            if m['maxp_sign'] is not None and m['maxp_value'] is not None:
                sign = '' if m['maxp_sign'] == '=' else m['maxp_sign']
                print >>o, "%w%d" % (sign,m['maxp_value']),

            if m['minp_sign'] is not None and m['minp_value'] is not None:
                sign = '' if m['minp_sign'] == '=' else m['minp_sign']
                print >>o, ",%s%d" % (sign,m['minp_value']),

            print >>o

        return o.getvalue()

    def dundi_conf(self):
        o = StringIO()

        print >>o, "[general]"
        general = self.backend.dundi.get(id=1)
        for k, v in general.iteritems():
            if v is None or k == 'id':
                continue

            if isinstance(v, unicode):
                v = v.encode('utf8')
            print >>o, k, "=", v

        trunks = dict([(t['id'], t) for t in self.backend.trunks.all()])

        print >>o, "\n[mappings]"
        for m in self.backend.dundimapping.all(commented=False):
            #dundi_context => local_context,weight,tech,dest[,options]]
            _t = trunks.get(m.trunk,{})
            _m = "%s => %s,%s,%s,%s:%s@%s/%s" % \
                    (m['name'],m['context'],m['weight'], 
                    _t.get('protocol','').upper(), _t.get('username',''),    _t.get('', 'secret'), 
                    _t['host']  if _t.get('host','dynamic') != 'dynamic' else '${IPADDR}',
                    m['number'] if m['number'] is not None else '${NUMBER}',
            )

            for k in ('nounsolicited','nocomunsolicit','residential','commercial','mobile','nopartial'):
                if m[k] == 1:
                    _m += ',' + k

            print >>o, _m

        # peers
        for p in self.backend.dundipeer.all(commented=False):
            print >>o, "\n[%s]" % p['macaddr']

            for k, v in p.iteritems():
                if k in ('id', 'macaddr','description','commented') or v is None:
                    continue

                print >>o, "%s = %s" % (k,v)

        return o.getvalue()

    def chan_dahdi_conf(self):
        o = StringIO()

        print >>o, "[channels]"
        for k, v in self.backend.dahdi.get(id=1).iteritems():
            if v is None or k == 'id':
                continue

            if isinstance(v, unicode):
                v = v.encode('utf8')
            print >>o, k, "=", v

        print >>o
        for group in self.backend.dahdigroup.all(commented=False):
            print >>o, "\ngroup=%d" % group['groupno']

            for k in ('context','switchtype','signalling','callerid','mailbox'):
                if group[k] is not None:
                    print >>o, k, "=", group[k]

            print >>o, "channel => %s" % group['channels']

        return o.getvalue()
