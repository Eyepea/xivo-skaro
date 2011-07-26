# -*- coding: UTF-8 -*-

"""Plugin for Cisco phones using the 9.2.1/SIP software."""

sipcommon = {}
execfile_('sipcommon.py', sipcommon)


MODELS = [u'8961', u'9951', u'9971']
VERSION = u'9.2.1/SIP'
MODEL_VERSION = dict((m, VERSION) for m in MODELS)


class CiscoSipPlugin(sipcommon['BaseCiscoSipPlugin']):
    IS_PLUGIN = True
    
    pg_associator = sipcommon['common']['BaseCiscoPgAssociator'](MODEL_VERSION)
