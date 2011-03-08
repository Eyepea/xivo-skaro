# -*- coding: UTF-8 -*-

"""Plugin for legacy Cisco phones using the SCCP software.

"""

common_globals = {}
execfile_('common.py', common_globals)


MODEL_VERSION = {u'7902G': u'8.0.2/SCCP',
                 u'7905G': u'8.0.3/SCCP',
                 u'7910G': u'5.0.7/SCCP',
                 u'7912G': u'8.0.4/SCCP',
                 u'7940G': u'8.1.2/SCCP',
                 u'7960G': u'8.1.2/SCCP'}


class CiscoSccpPlugin(common_globals['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)
