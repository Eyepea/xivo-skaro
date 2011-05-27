# -*- coding: UTF-8 -*-

"""Plugin for various Gigaset using the 025 firmware.

The following Gigaset phones are supported:
- C590 IP
- C595 IP (not tested)
- C610 IP (not tested)
- C610A IP (not tested)
- N300 IP (not tested)
- N300A IP (not tested)
- N510 IP PRO (not tested)

"""

import logging
import re

common_globals = {}
execfile_('common.py', common_globals)

logger = logging.getLogger('plugin.xivo-gigaset')


MODELS = [u'C590 IP', u'C595 IP', u'C610 IP', u'C610A IP', u'N300 IP',
          u'N300A IP', u'N510 IP PRO']


class GigasetRequestBroker(common_globals['BaseGigasetRequestBroker']):
    _VERSION_REGEX = re.compile(r'\b42(\d{3})')
    
    def disable_gigasetnet_line(self):
        # we need to first check if the line is enabled or not...
        with self.do_get_request('scripts/settings_telephony_voip_multi.js') as fobj:
            for line in fobj:
                if line.startswith('linesSHC[0][4]='):
                    if line[12:13] == '3':
                        logger.debug('gigaset line is enabled')
                        break
                    else:
                        logger.debug('gigaset line is disabled')
                        return
            else:
                raise GigasetInteractionError('Could not determine gigaset line status')
        
        # assert: gigaset line is enabled
        raw_data = 'account_id=6&action_type=1'
        with self.do_post_request('settings_telephony_connections.html', raw_data) as fobj:
            fobj.read()
    
    def set_mailboxes(self, dict_):
        # dict_ is a dictionary where keys are line number and values are
        # mailbox extensions number
        raw_data = {}
        for id_no in xrange(8):
            line_no = id_no + 1
            if line_no in dict_:
                raw_data['ad_number_%s' % id_no] = voicemail
                raw_data['ad_active_%s' % id_no] = 'on'
            else:
                raw_data['ad_number_%s' % id_no] = ''
        with self.do_post_request('settings_telephony_network_mailboxes.html', raw_data) as fobj:
            fobj.read()


class GigasetPlugin(common_globals['BaseGigasetPlugin']):
    IS_PLUGIN = True
    
    _BROKER_FACTORY = GigasetRequestBroker
    
    pg_associator = common_globals['BaseGigasetPgAssociator'](MODELS)
