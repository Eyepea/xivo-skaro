# -*- coding: UTF-8 -*-

"""Plugin for Cisco phones using the 9.0.3/SCCP software.

"""

common_globals = {}
execfile_('common.py', common_globals)


VENDOR = 'Cisco'
MODELS = ['7906G', '7911G', '7931G', '7941G', '7942G', '7945G', '7961G',
          '7962G', '7965G', '7970G', '7971G', '7975G']
VERSION = '9.0.3/SCCP'

class CiscoSccpPlugin(common_globals['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    device_types = [(VENDOR, model, VERSION) for model in MODELS]
