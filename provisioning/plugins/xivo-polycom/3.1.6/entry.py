# -*- coding: UTF-8 -*-

"""Plugin for Polycom phones using the 3.1.6.0017 SIP application.

The following Polycom phones are supported:
- SPIP301
- SPIP501
- SPIP600
- SPIP601
- SSIP4000

"""

common_globals = {}
execfile_('common.py', common_globals)


MODELS = [u'SPIP301', u'SPIP501', u'SPIP600', u'SPIP601', u'SSIP4000']
VERSION = u'3.1.6.0017'


class PolycomPlugin(common_globals['BasePolycomPlugin']):
    IS_PLUGIN = True
    
    _XX_LANGUAGE_MAP = {
        u'de_DE': u'German_Germany',
        u'en_US': u'English_United_States',
        u'es_ES': u'Spanish_Spain',
        u'fr_FR': u'French_France',
        u'fr_CA': u'French_France',
    }
    
    pg_associator = common_globals['BasePolycomPgAssociator'](MODELS, VERSION)
