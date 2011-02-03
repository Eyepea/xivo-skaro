# -*- coding: UTF-8 -*-

"""Plugin for legacy Cisco SPA phones. This include every Linksys branded
phones.

The following Cisco phones are supported:
- SPA901
- SPA921
- SPA922
- SPA941
- SPA942
- SPA962

The following Cisco expansion module are supported:
- SPA932

"""

common_globals = {}
execfile_('common.py', common_globals)


MODEL_VERSION = {'SPA901': '5.1.5',
                 'SPA921': '5.1.8',
                 'SPA922': '6.1.5(a)',
                 'SPA941': '5.1.8',
                 'SPA942': '6.1.5(a)',
                 'SPA962': '6.1.5(a)'}


class CiscoPlugin(common_globals['BaseCiscoPlugin']):
    IS_PLUGIN = True
    _COMMON_FILENAMES = [model.lower() + '.cfg' for model in MODEL_VERSION]
    
    pg_associator = common_globals['BaseCiscoPgAssociator'](MODEL_VERSION)
