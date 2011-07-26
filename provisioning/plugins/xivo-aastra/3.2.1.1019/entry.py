# -*- coding: UTF-8 -*-

"""Plugin for Aastra phones using the 3.2.1.1019 software.

The following Aastra phones are supported:
- 6730i
- 6731i
- 6739i
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
- 6751i

"""

import logging

common = {}
execfile_('common.py', common)

logger = logging.getLogger('plugin.xivo-aastra')


MODELS = [u'6730i', u'6731i', u'6739i', u'6753i', u'6755i', u'6757i',
          u'9143i', u'9480i']
COMPAT_MODELS = [u'6751i']
VERSION = u'3.2.1.1019'


class AastraPlugin(common['BaseAastraPlugin']):
    IS_PLUGIN = True
    
    pg_associator = common['BaseAastraPgAssociator'](MODELS, VERSION,
                                                     COMPAT_MODELS)

    def _do_add_parking(self, raw_config, parking):
        raw_config[u'XX_parking'] = '\n'.join('sip line%s park pickup config: %s;%s;asterisk' %
                                              (line_no, parking, parking)
                                              for line_no in raw_config[u'sip_lines'])
    
    def _add_parking(self, raw_config):
        # hack to set the per line parking config if a park function key is used
        parking = None
        is_parking_set = False
        for funckey_no, funckey_dict in raw_config[u'funckeys'].iteritems():
            if funckey_dict[u'type'] == u'park':
                if is_parking_set:
                    cur_parking = funckey_dict[u'value']
                    if cur_parking != parking:
                        logger.warning('Ignoring park value %s for function key %s: using %s',
                                       cur_parking, funckey_no, parking)
                else:
                    parking = funckey_dict[u'value']
                    is_parking_set = True
                    self._do_add_parking(raw_config, parking)
