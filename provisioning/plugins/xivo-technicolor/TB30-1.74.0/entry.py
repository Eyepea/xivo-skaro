# -*- coding: UTF-8 -*-

"""Plugin for Technicolor TB30 using the 1.74.0 SIP firmware."""

common_globals = {}
execfile_('common.py', common_globals)


MODEL = 'TB30'
VERSION = '1.74.0'


class TechnicolorPlugin(common_globals['BaseTechnicolorPlugin']):
    IS_PLUGIN = True
    
    _COMMON_TEMPLATES = [('common/TB30S.inf.tpl', 'TB30S.inf')]
    _FILENAME_PREFIX = 'TB30S'
    
    pg_associator = common_globals['BaseTechnicolorPgAssociator'](MODEL, VERSION)
