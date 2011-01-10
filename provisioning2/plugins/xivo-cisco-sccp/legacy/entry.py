# -*- coding: UTF-8 -*-

"""Plugin for legacy Cisco phones using the SCCP software.

"""

common_globals = {}
execfile_('common.py', common_globals)


MODEL_VERSION = {'7902G': '8.0.2/SCCP',
                 '7905G': '8.0.3/SCCP',
                 '7910G': '5.0.7/SCCP',
                 '7912G': '8.0.4/SCCP',
                 '7940G': '8.1.2/SCCP',
                 '7960G': '8.1.2/SCCP'}


class CiscoSccpPlugin(common_globals['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)
