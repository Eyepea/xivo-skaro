# -*- coding: UTF-8 -*-

"""Plugin for Cisco phones using the 9.0.3/SCCP software.

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = ['7906G', '7911G', '7931G', '7941G', '7942G', '7945G', '7961G',
          '7962G', '7965G', '7970G', '7971G', '7975G']
VERSION = '9.0.3/SCCP'
MODEL_VERSION = dict((m, VERSION) for m in MODELS)


class CiscoSccpPlugin(common_globals['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)
