# -*- coding: UTF-8 -*-

"""Plugin for Cisco SPA phones using the 7.4.7 firmware.

The following Cisco phones are supported:
- SPA301
- SPA303
- SPA501G
- SPA502G
- SPA504G
- SPA508G
- SPA509G
- SPA525G

The following Cisco expansion module are supported:
- SPA500S

"""

common_globals = {}
execfile_('common.py', common_globals)


PSN = ['301', '303', '501G', '502G', '504G', '508G', '509G', '525G']
MODELS = ['SPA' + psn for psn in PSN]
MODEL_VERSION = dict((model, '7.4.7') for model in MODELS)


class CiscoPlugin(common_globals['BaseCiscoPlugin']):
    IS_PLUGIN = True
    # similar to spa508G.cfg (G is uppercase)
    _COMMON_FILENAMES = ['spa' + psn + '.cfg' for psn in PSN]
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)
    
