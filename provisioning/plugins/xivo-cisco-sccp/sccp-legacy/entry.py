# -*- coding: UTF-8 -*-

"""Plugin for legacy Cisco phones using the SCCP software."""

sccpcommon = {}
execfile_('sccpcommon.py', sccpcommon)


MODEL_VERSION = {u'7902G': u'8.0.2/SCCP',
                 u'7905G': u'8.0.3/SCCP',
                 u'7910G': u'5.0.7/SCCP',
                 u'7912G': u'8.0.4/SCCP',
                 u'7940G': u'8.1.2/SCCP',
                 u'7960G': u'8.1.2/SCCP'}


class CiscoSccpPlugin(sccpcommon['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = sccpcommon['common']['BaseCiscoPgAssociator'](MODEL_VERSION)
