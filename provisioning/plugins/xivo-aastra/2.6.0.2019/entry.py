# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 2.6.0.2019 software.

The following Aastra phones are supported:
- 6730i
- 6731i
- 6751i
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
- 6739i

"""

common = {}
execfile_('common.py', common)


MODELS = [u'6730i', u'6731i', u'6751i', u'6753i', u'6755i', u'6757i',
          u'9143i', u'9480i']
COMPAT_MODELS = [u'6739i']
VERSION = u'2.6.0.2019'


class AastraPlugin(common['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common['BaseAastraPgAssociator'](MODELS, VERSION,
                                                     COMPAT_MODELS)
