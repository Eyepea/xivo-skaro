import base64
import struct
import zlib

class Sheet:
    def __init__(self, where, ipbxid, channel):
        self.internaldata = { 'where' : where,
                              'ipbxid' : ipbxid,
                              'channel' : channel }
        self.linestosend = []
        self.options = {}
        return

    def setoptions(self, options):
        self.options = options
        return

    def addinternal(self, varname, varvalue):
        self.linestosend.append('<internal name="%s"><![CDATA[%s]]></internal>'
                                % (varname, varvalue))
        return

    def makexml(self):
        self.linestosend = []
        self.linestosend = ['<?xml version="1.0" encoding="utf-8"?>',
                            '<profile>',
                            '<user>']
        for k, v in self.internaldata.iteritems():
            self.addinternal(k, v)
        for k, v in self.options.iteritems():
            self.addinternal(k, v)

        self.linestosend.append('<%s order="%s" name="%s" type="%s"><![CDATA[%s]]></%s>'
                                % ("sheet_info", 34, "op", "text", "gaga", "sheet_info"))

##        linestosend.extend(self.__build_xmlqtui__('sheet_qtui', actionopt, itemdir))
##        linestosend.extend(self.__build_xmlsheet__('action_info', actionopt, itemdir))
##        linestosend.extend(self.__build_xmlsheet__('sheet_info', actionopt, itemdir))
##        linestosend.extend(self.__build_xmlsheet__('systray_info', actionopt, itemdir))

        self.linestosend.extend(['</user>', '</profile>'])
        return

    def buildpayload(self):
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
