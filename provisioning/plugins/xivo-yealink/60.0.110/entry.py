# -*- coding: UTF-8 -*-

"""Plugin for Yealink phones using the 60.0.110 firmware.

The following Yealink phones are supported:
- T12P
- T20P
- T22P
- T26P
- T28P

"""

common_globals = {}
execfile_('common.py', common_globals)


MODEL_VERSIONS = {u'T12P': u'5.60.0.110',
                  u'T20P': u'9.60.0.100',
                  u'T22P': u'7.60.0.110',
                  u'T26P': u'6.60.0.110',
                  u'T28P': u'2.60.0.110'}
COMMON_FILES = [('y000000000000.cfg', u'2.60.0.110.rom'),
                ('y000000000004.cfg', u'6.60.0.110.rom'),
                ('y000000000005.cfg', u'7.60.0.110.rom'),
                ('y000000000007.cfg', u'9.60.0.110.rom'),
                ('y000000000008.cfg', u'5.60.0.110.rom')]


class YealinkPlugin(common_globals['BaseYealinkPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common_globals['BaseYealinkPgAssociator'](MODEL_VERSIONS)

    # Yealink plugin specific stuff
    
    _COMMON_FILES = COMMON_FILES
