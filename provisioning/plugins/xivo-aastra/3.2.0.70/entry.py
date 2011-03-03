# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 2.6.0.2010 software.

The following Aastra phones are supported:
- 6730i
- 6731i
- 6739i
- 6753i
- 6755i
- 6757i / 6757i CT
- 9143i
- 9480i / 9480i CT

The following Aastra expansion modules are supported:
- M670i
- M675i

The following Aastra phones are NOT officially supported, although they should
work with this plugin:
- 6751i

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = ['6730i', '6731i', '6739i', '6753i', '6755i', '6757i', '9143i', '9480i']
COMPAT_MODELS = ['6751i']
VERSION = '3.2.0.70'


class AastraPlugin(common_globals['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseAastraPgAssociator'](MODELS, VERSION,
                                                             COMPAT_MODELS)
