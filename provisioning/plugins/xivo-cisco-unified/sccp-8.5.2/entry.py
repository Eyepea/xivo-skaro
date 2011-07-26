# -*- coding: UTF-8 -*-

"""Plugin for Cisco phones using the 8.5.2/SCCP software."""

sccpcommon = {}
execfile_('sccpcommon.py', sccpcommon)


MODELS = [u'7906G', u'7911G', u'7931G', u'7941G', u'7942G', u'7945G', u'7961G',
          u'7962G', u'7965G', u'7970G', u'7971G', u'7975G']
VERSION = u'8.5.2/SCCP'
MODEL_VERSION = dict((m, VERSION) for m in MODELS)


class CiscoSccpPlugin(sccpcommon['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = sccpcommon['common']['BaseCiscoPgAssociator'](MODEL_VERSION)
