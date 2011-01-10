# -*- coding: UTF-8 -*-

"""Plugin for Snom phones using the 8.4.18 software.

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = ['300', '320', '360', '370', '820', '821', '870']
COMPAT_MODELS = ['MeetingPoint']
VERSION = '8.4.18'


class SnomPlugin(common_globals['BaseSnomPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseSnomPgAssociator'](MODELS, VERSION,
                                                           COMPAT_MODELS)
