#!/usr/bin/python
# -*- coding: utf-8 -*-

import cjson
import getopt
import hashlib
import random
import select
import socket
import string
import sys
import time
import urllib

server_address = '127.0.0.1'
server_port = '5003'
scenario = None

__alphanums__ = string.uppercase + string.lowercase + string.digits

GETOPT_SHORTOPTS = 'a:p:s:'
GETOPT_LONGOPTS = ['address=', 'port=', 'scenario=']

opts = getopt.gnu_getopt(sys.argv[1:],
                         GETOPT_SHORTOPTS,
                         GETOPT_LONGOPTS)
for opt, arg in opts[0]:
    if opt in ['-a', '--address']:
        server_address = arg
    elif opt in ['-p', '--port']:
        server_port = arg
    elif opt in ['-s', '--scenario']:
        scenario = arg

def makepacket(classname, user, *args):
    if classname == 'login_id':
        mydict = { 'lastlogout-datetime' : '2009-12-02T17:43:24',
                   'lastlogout-stopper' : 'quit',
                   'company' : 'default',
                   'userlogin' : user.get('userlogin'),
                   'git_hash' : 'zzz',
                   'git_date' : '000',
                   'ident' : 'X11-LE-17131',
                   'xivoversion' : '1.2',
                   'version' : '7187'
                   }
    elif classname == 'login_pass':
        tohash = '%s:%s' % (args[0], user.get('password'))
        mydict = { 'hashedpassword' : hashlib.sha1(tohash).hexdigest() }
    elif classname == 'login_capas':
        mydict = { 'lastconnwins' : False,
                   'capaid' : args[0][0],
                   'loginkind' : 'user',
                   'state' : ''
                   }
    mydict['class'] = classname
    mypack = cjson.encode(mydict) + '\n'
    return mypack

# per connection : who (properties), socket, state diagram
# TODO : define appropriate list (cf. WEBI ?) + try to avoid those who are already connected
# TODO : use for "agent login/logout" actions
# TODO : use random features, such as which action or which agent

# ./tools/cticlient.py -a 192.168.0.252

users = []
##f = urllib.urlopen('https://%s/service/ipbx/json.php/restricted/pbx_settings/users' % server_address)
##h = f.read()
##f.close()
##hh = cjson.decode(h)
##for uu in hh:
##    if uu.get('loginclient'):
##        nu = {
##            'userid' : uu.get('loginclient'),
##            'password' : uu.get('passwdclient')
##            }
##        idnum = uu.get('id')
##        if idnum not in ['2', '4', '16', '32', '49', '57', '62', '63', '79']:
##        # if idnum not in ['2', '4', '16', '32', '57', '62', '63']:
##            print nu, uu.get('id')
##            users.append(nu)
##        else:
##            nu2 = nu
##            nu2['password'] = 'krkrkr'
##            users.append(nu2)

users = []
for n in ['edeislkovqmlcd',
          ]:
    users.append( {'userlogin' : n,
                   'password' : n[7].upper() + n[8:]}
                  )

corr = {}
for n in users:
    print server_address, int(server_port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_address, int(server_port)))
    corr[s] = n

ipbxcommandstotest = []
if scenario:
    t = open(scenario, 'r')
    e = t.read()
    t.close()
    ipbxcommandstotest = e.split('\n')

# meetme is regcommand, not ipbxcommand (?)
# regcommand parking vs. ipbxcommand park ?

while True:
    try:
        [sels_i, sels_o, sels_e] = select.select(corr.keys(), [], [], 10)
        if sels_i:
            for sel_i in sels_i:
                reply = sel_i.recv(8192).strip()
                banner = False
                if reply:
                    try:
                        dreply = cjson.decode(reply)
                        ctype = dreply.get('class')
                        print 'got class', ctype
                    except Exception, te:
                        if te.message == 'cannot parse JSON description':
                            banner = True
                if sel_i in corr:
                    user = corr[sel_i]
                if banner:
                    sel_i.sendall(makepacket('login_id', user))
                else:
                    if ctype == 'login_id':
                        sel_i.sendall(makepacket('login_pass', user, dreply.get('sessionid')))
                    elif ctype == 'login_pass':
                        sel_i.sendall(makepacket('login_capas', user, dreply.get('capalist')))
                    else:
                        classname = 'ipbxcommand'
                        if ipbxcommandstotest:
                            commandtotest = ipbxcommandstotest.pop(0)
                            if commandtotest:
                                commandtotest_spc = commandtotest.split()
                                rn = ''.join(random.sample(__alphanums__, 10))
                                ct = { 'class' : classname,
                                       'commandid' : 'cc-%s' % rn }
                                for ctt in commandtotest_spc:
                                    [k, v] = ctt.split('=', 1)
                                    ct[k] = v
                                print ct
                                gg = cjson.encode(ct)
                                sel_i.sendall(gg + '\n')
        else:
            print 'timeout'
    except Exception, exc:
        print exc
