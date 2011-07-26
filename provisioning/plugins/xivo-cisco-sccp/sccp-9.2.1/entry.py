# -*- coding: UTF-8 -*-

"""Plugin for Cisco phones using the 9.2.1/SCCP software."""

sccpcommon = {}
execfile_('sccpcommon.py', sccpcommon)


MODELS = [u'6901', u'6911', u'6921', u'6941', u'6945', u'6961', u'7906G',
          u'7911G', u'7931G', u'7941G', u'7942G', u'7945G', u'7961G',
          u'7962G', u'7965G', u'7970G', u'7971G', u'7975G']
VERSION = u'9.2.1/SCCP'
MODEL_VERSION = dict((m, VERSION) for m in MODELS)


class CiscoSccpPlugin(sccpcommon['BaseCiscoSccpPlugin']):
    IS_PLUGIN = True
    
    pg_associator = sccpcommon['common']['BaseCiscoPgAssociator'](MODEL_VERSION)
