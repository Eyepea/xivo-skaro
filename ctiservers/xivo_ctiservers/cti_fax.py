# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011  Avencall
__author__    = 'Corentin Le Gall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64
import commands
import logging
import os
import threading
import time

PATH_SPOOL_ASTERISK     = '/var/spool/asterisk'
PATH_SPOOL_ASTERISK_FAX = PATH_SPOOL_ASTERISK + '/fax'
PATH_SPOOL_ASTERISK_TMP = PATH_SPOOL_ASTERISK + '/tmp'
PDF2FAX = '/usr/bin/xivo_pdf2fax'

class asyncActionsThread(threading.Thread):
    def __init__(self, name, params):
        threading.Thread.__init__(self)
        self.setName(name)
        self.params = params
        fileid = self.params.get('fileid')
        self.log = logging.getLogger('async(%s)' % fileid)
        return

    def decodefile(self):
        decodedfile = base64.b64decode(self.params.get('rawfile').strip())
        filename = 'astsendfax-%s' % self.params.get('fileid')
        self.tmpfilepath = '%s/%s' % (PATH_SPOOL_ASTERISK_TMP, filename)
        z = open(self.tmpfilepath, 'w')
        z.write(decodedfile)
        z.close()
        return

    def converttotiff(self):
        reply = 'ko;unknown'
        comm = commands.getoutput('file -b %s' % self.tmpfilepath)
        brieffile = ' '.join(comm.split()[0:2])
        if brieffile == 'PDF document,':
            self.faxfilepath = self.tmpfilepath + '.tif'
            pdf2fax_command = '%s -o %s %s' % (PDF2FAX, self.faxfilepath, self.tmpfilepath)
            self.log.info('(ref %s) PDF to TIF(F) : %s' % (self.tmpfilepath, pdf2fax_command))
            reply = 'ko;convert-pdftif'
            sysret = os.system(pdf2fax_command)
            ret = os.WEXITSTATUS(sysret)
            if ret:
                self.log.warning('(ref %s) PDF to TIF(F) returned : %s (exitstatus = %s, stopsignal = %s)'
                                 % (self.tmpfilepath, sysret, ret, os.WSTOPSIG(sysret)))
            else:
                reply = 'ok;'
        else:
            reply = 'ko;filetype'
            self.log.warning('(ref %s) the file received is a <%s> one : format not supported'
                             % (self.reference, brieffile))
            ret = -1
        print reply
        os.unlink(self.tmpfilepath)
        return

    def notify_step(self, stepname):
        innerdata = self.params.get('innerdata')
        fileid = self.params.get('fileid')
        innerdata.cb_timer({'action' : 'fax',
                            'properties' : {'step' : stepname,
                                            'fileid' : fileid}},)
        return

    def run(self):
        self.decodefile()
        self.notify_step('file_decoded')
        self.converttotiff()
        self.notify_step('file_converted')
        self.log.info('%s thread is over' % self.getName())
        return



class Fax:
    def __init__(self, innerdata, fileid):
        self.innerdata = innerdata
        self.fileid = fileid
        self.log = logging.getLogger('fax(%s)' % self.fileid)

        filename = 'astsendfax-%s' % self.fileid
        self.faxfilepath = '%s/%s.tif' % (PATH_SPOOL_ASTERISK_TMP, filename)
        return

    def setfaxparameters(self, userid, context, number, hide):
        self.userid = userid
        self.context = context
        self.number = number.replace('.', '').replace(' ', '')
        if hide != '0':
            self.callerid = 'anonymous'
        else:
            self.callerid = '010101'
        return

    def setfileparameters(self, size):
        self.size = size
        return

    def setsocketref(self, socketref):
        self.socketref = socketref
        return

    def setrequester(self, requester):
        self.requester = requester
        return

    def setbuffer(self, rawfile):
        """Set on the 2nd opened soocket"""
        self.rawfile = rawfile
        return

    def launchasyncs(self):
        sthread = asyncActionsThread('fax-%s' % self.fileid,
                                     { 'innerdata' : self.innerdata,
                                       'fileid' : self.fileid,
                                       'rawfile' : self.rawfile
                                       } )
        sthread.start()
        return

    def step(self, stepname):
        removeme = False
        try:
            self.requester.reply( { 'class' : 'faxsend',
                                    'fileid' : self.fileid,
                                    'step' : stepname
                                    } )
        except Exception:
            # when requester is not connected any more ...
            pass

        if stepname == 'file_converted':
            removeme = True

        return removeme

    def getparams(self):
        params = {
            'mode' : 'useraction',
            'request' : {
                'requester' : self.requester,
                'ipbxcommand' : 'sendfax',
                'commandid' : self.fileid
                },
            'amicommand' : 'txfax',
            'amiargs' : (self.faxfilepath,
                         self.userid,
                         self.callerid,
                         self.number,
                         self.context)
            }
        return params
