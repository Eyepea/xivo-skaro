# -*- coding: UTF-8 -*-

"""Plugin for Alcatel phones using the SIP 2.01.10 firmware.

The following Alcatel "extended edition" phones are supported:
- 4008
- 4018

"""

import logging

common_globals = {}
execfile_('common.py', common_globals)

logger = logging.getLogger('plugin.xivo-alcatel')

MODELS = [u'4008', u'4018']
VERSION = u'2.01.10'


class AlcatelPlugin(common_globals['BaseAlcatelPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseAlcatelPgAssociator'](MODELS, VERSION)
