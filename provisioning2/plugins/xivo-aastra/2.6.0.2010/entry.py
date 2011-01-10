# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 2.6.0.2010 software.

The following Aastra phones are supported:
- 6730i
- 6731i
- 6751i
- 6753i
- 6755i
- 6757i

The following Aastra expansion modules are supported:
- M670i
- M675i

The following Aastra phones are NOT officially supported, although they should
work with this plugin:
- 9143i
- 9480i
- 6739i

# TODO we should probably specify/document...
#     ...which devices this plugin can identify, and how
#     ...which config parameter the plugin use, and how
#     but it might be more useful to document this in a separate file or on
#     the wiki then inside this file...

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = ['6730i', '6731i', '6751i', '6753i', '6755i', '6757i']
COMPAT_MODELS = ['6739i', '9143i', '9480i']
VERSION = '2.6.0.2010'


class AastraPlugin(common_globals['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseAastraPgAssociator'](MODELS, VERSION,
                                                             COMPAT_MODELS)
