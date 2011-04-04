# -*- coding: UTF-8 -*-

"""Plugin for Technicolor ST2030 using the 2.74 SIP firmware."""

common_globals = {}
execfile_('common.py', common_globals)


MODEL = 'ST2030'
VERSION = '2.74'


class TechnicolorPlugin(common_globals['BaseTechnicolorPlugin']):
    IS_PLUGIN = True
    
    _COMMON_TEMPLATES = [('common/ST2030S.inf.tpl', 'ST2030S.inf')]
    _FILENAME_PREFIX = 'ST2030S'
    
    pg_associator = common_globals['BaseTechnicolorPgAssociator'](MODEL, VERSION)
