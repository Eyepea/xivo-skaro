# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 3.0.1.2031 firmware.

The following Aastra phones are supported:
- 6739i

The following Aastra expansion modules are supported:
- M670i
- M675i

The following Aastra phones are NOT officially supported, although they should
work with this plugin:
- 6730i
- 6731i
- 6751i
- 6753i
- 6755i
- 6757i
- 9143i
- 9480i

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = [u'6739i']
COMPAT_MODELS = [u'6730i', u'6731i', u'6751i', u'6753i', u'6755i', u'6757i',
                 u'9143i', u'9480i']
VERSION = u'3.0.1.2031'


class AastraPlugin(common_globals['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseAastraPgAssociator'](MODELS, VERSION,
                                                             COMPAT_MODELS)
