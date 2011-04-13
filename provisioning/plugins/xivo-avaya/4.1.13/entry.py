# -*- coding: UTF-8 -*-

"""Plugin for Avaya 1220IP and 1230IP using the 04.01.13.00 SIP software."""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = [u'1220IP', u'1230IP']
VERSION = u'04.01.13.00'


class AvayaPlugin(common_globals['BaseAvayaPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseAvayaPgAssociator'](MODELS, VERSION)
