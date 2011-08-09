# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 3.0.1.2031 firmware.

The following Aastra phones are supported:
- 6739i

"""

common = {}
execfile_('common.py', common)


MODELS = [u'6739i']
COMPAT_MODELS = [u'6730i', u'6731i', u'6751i', u'6753i', u'6755i', u'6757i',
                 u'9143i', u'9480i']
VERSION = u'3.0.1.2031'


class AastraPlugin(common['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common['BaseAastraPgAssociator'](MODELS, VERSION,
                                                     COMPAT_MODELS)
