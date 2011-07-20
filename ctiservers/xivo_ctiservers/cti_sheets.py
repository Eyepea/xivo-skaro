# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011 Proformatique'
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
import struct
import urllib
import zlib

class Sheet:
    def __init__(self, where, ipbxid, channel):
        self.internaldata = { 'where' : where,
                              'ipbxid' : ipbxid,
                              'channel' : channel }
        # config items
        self.options = {}
        self.displays = {}
        # temporary structure
        self.fields = {}
        # output
        self.linestosend = []
        return

    def setoptions(self, options):
        if options:
            self.options = options
        return

    def setdisplays(self, displays):
        if displays:
            self.displays = displays
        return

    def addinternal(self, varname, varvalue):
        self.linestosend.append('<internal name="%s"><![CDATA[%s]]></internal>'
                                % (varname, varvalue))
        return

    def buildresult(self, lineprops):
        [title, ftype, defaultval, sformat] = lineprops
        finalstring = sformat
        for k, v in self.channelprops.extra_data.iteritems():
            for kk, vv in v.iteritems():
                variablename = '{%s-%s}' % (k, kk)
                finalstring = finalstring.replace(variablename, vv)
        if finalstring.find('{xivo-callerpicture}') >= 0:
            userid = self.channelprops.extra_data.get('xivo').get('userid')
            url = 'https://127.0.0.1/getatt.php?id=%s&obj=user' % userid
            try:
                picture_desc = urllib.urlopen(url)
                picture_data = picture_desc.read()
                picture_desc.close()
            except:
                picture_data = ''
            # remove the '\x' char from the beginning of the resulting data
            # and encode the binary in base64 : data length changes from 1 to 1/2 to 3/4
            b64value = base64.b64encode(base64.b16decode(picture_data[2:].upper()))
            finalstring = b64value

        result = { 'name' : title,
                   'type': ftype,
                   'contents' : finalstring }
        return result

    def setfields(self):
        for sheetpart, v in self.displays.iteritems():
            self.fields[sheetpart] = {}
            if sheetpart in ['sheet_info', 'systray_info', 'action_info']:
                if not isinstance(v, dict):
                    continue
                for order, vv in v.iteritems():
                    self.fields[sheetpart][order] = self.buildresult(vv)
            elif sheetpart == 'sheet_qtui':
                for order, vv in v.iteritems():
                    try:
                        qtui_desc = urllib.urlopen(vv)
                        qtui_data = qtui_desc.read().decode('utf8')
                        qtui_desc.close()
                    except Exception:
                        qtui_data = ''
                    self.fields[sheetpart] = {'ui' : {'name' : 'qtui',
                                                      'contents' : qtui_data}}
            else:
                print 'unknown', sheetpart, v
        # print self.fields
        # linestosend.extend(self.__build_xmlqtui__('sheet_qtui', actionopt, itemdir))
        return

    def serialize(self):
        if True:
            self.makexml()
        else:
            self.makejson()

    def makexml(self):
        self.serial = 'xml'
        self.linestosend = []
        self.linestosend = ['<?xml version="1.0" encoding="utf-8"?>',
                            '<profile>',
                            '<user>']
        for k, v in self.internaldata.iteritems():
            self.addinternal(k, v)

        for k, v in self.options.iteritems():
            self.addinternal(k, v)

        # making sure that 'sheet_qtui' is the first in the line, if ever we send it
        # quite long stuff for that, but feel free to shorten it
        sfkeys = self.fields.keys()
        if 'sheet_qtui' in sfkeys:
            sfkeys.pop(sfkeys.index('sheet_qtui'))
            sfkeys.insert(0, 'sheet_qtui')
        for sheetpart in sfkeys:
            v = self.fields.get(sheetpart)
            for order, vv in v.iteritems():
                title = vv.get('name')
                ftype = vv.get('type')
                contents = vv.get('contents')
                self.linestosend.append('<%s order="%s" name="%s" type="%s"><![CDATA[%s]]></%s>'
                                        % (sheetpart, order, title, ftype, contents, sheetpart))
        self.linestosend.extend(['</user>', '</profile>'])

        self.xmlstring = ''.join(self.linestosend).encode('utf8')
        if self.options.get('zip', True):
            ulen = len(self.xmlstring)
            # prepend the uncompressed length in big endian
            # to the zlib compressed string to meet Qt qUncompress() function expectations
            toencode = struct.pack('>I', ulen) + zlib.compress(self.xmlstring)
            self.payload = base64.b64encode(toencode)
            self.compressed = True
        else:
            self.payload = base64.b64encode(self.xmlstring)
            self.compressed = False
        return

    def makejson(self):
        self.serial = 'json'
        self.compressed = False
        self.payload = { 'internal' : self.internaldata,
                         'fields' : self.fields }
        return

    def setconditions(self, conditions):
        self.conditions = conditions

    def checkdest(self, channelprops):
        self.channelprops = channelprops
        whom = self.conditions.get('whom')
        entities = self.conditions.get('entities')
        contexts = self.conditions.get('contexts')
        profileids = self.conditions.get('profileids')

        tomatch = dict()
        if profileids:
            tomatch['profileids'] = profileids
        if contexts:
            tomatch['contexts'] = contexts
        if entities:
            tomatch['entities'] = entities

        if whom == 'dest':
            tomatch['desttype'] = channelprops.extra_data.get('xivo').get('desttype')
            tomatch['destid'] = channelprops.extra_data.get('xivo').get('destid')

        return tomatch
