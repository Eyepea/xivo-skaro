import base64
import struct
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

    def setfields(self):
        for sheetpart, v in self.displays.iteritems():
            self.fields[sheetpart] = {}
            if sheetpart in ['sheet_info', 'systray_info', 'action_info']:
                if not isinstance(v, dict):
                    continue
                for order, vv in v.iteritems():
                    [title, ftype, defaultval, sformat] = vv
                    ## XXX TODO : replace sformat/defaultval with variables stuff
                    self.fields[sheetpart][order] = { 'name' : title,
                                                      'type': ftype,
                                                      'contents' : sformat }
            else:
                print sheetpart, v
##        linestosend.extend(self.__build_xmlqtui__('sheet_qtui', actionopt, itemdir))
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

        for sheetpart, v in self.fields.iteritems():
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
            toencode = struct.pack(">I", ulen) + zlib.compress(self.xmlstring)
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
