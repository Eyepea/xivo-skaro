# -*- coding: UTF-8 -*-

"""Plugin for Technicolor ST2022 using the 4.69.2 SIP firmware."""

common_globals = {}
execfile_('common.py', common_globals)


MODEL = 'ST2022'
VERSION = '4.69.2'


class TechnicolorPlugin(common_globals['BaseTechnicolorPlugin']):
    IS_PLUGIN = True
    
    _COMMON_TEMPLATES = [('common/ST2022S.inf.tpl', 'ST2022S.inf')]
    _FILENAME_PREFIX = 'ST2022S'
    
    pg_associator = common_globals['BaseTechnicolorPgAssociator'](MODEL, VERSION)
