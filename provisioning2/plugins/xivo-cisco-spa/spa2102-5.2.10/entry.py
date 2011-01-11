# -*- coding: UTF-8 -*-

"""Plugin for Cisco 2102 in version 5.2.10."""

common_globals = {}
execfile_('common.py', common_globals)


MODEL_VERSION = {'SPA2102': '5.2.10'}


class CiscoPlugin(common_globals['BaseCiscoPlugin']):
    IS_PLUGIN = True
    _COMMON_FILENAMES = ['spa2102.cfg']
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)