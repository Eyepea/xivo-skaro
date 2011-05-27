# -*- coding: UTF-8 -*-

"""Plugin for various Gigaset using the 02227 firmware.

The following Gigaset phones are supported:
- C470 IP
- C475 IP (not tested)
- S675 IP
- S685 IP (not tested)

"""

import logging
import re

common_globals = {}
execfile_('common.py', common_globals)

logger = logging.getLogger('plugin.xivo-gigaset')


MODELS = [u'C470 IP', u'C475 IP', u'S675 IP', u'S685 IP']


class GigasetRequestBroker(common_globals['BaseGigasetRequestBroker']):
    _VERSION_REGEX = re.compile(r'\b02(\d{3})')
    
    def disable_gigasetnet_line(self):
        # we need to first check if the line is enabled or not...
        with self.do_get_request('scripts/settings_telephony_voip_multi.js') as fobj:
            for line in fobj:
                if line.startswith('lines[6][4]='):
                    if line[12:13] == '1':
                        logger.debug('gigaset line is enabled')
                        break
                    else:
                        logger.debug('gigaset line is disabled')
                        return
            else:
                raise GigasetInteractionError('Could not determine gigaset line status')
        
        # assert: gigaset line is enabled
        raw_data = 'account_id=6'
        with self.do_post_request('settings_telephony_voip_multi.html', raw_data) as fobj:
            fobj.read()
    
    def set_mailboxes(self, dict_):
        # dict_ is a dictionary where keys are line number and values are
        # mailbox extensions number
        raw_data = {}
        for id_no in xrange(7):
            line_no = id_no + 1
            if line_no in dict_:
                raw_data['ad1_%s' % id_no] = dict_[line_no]
                raw_data['ad2_%s' % id_no] = 'on'
            else:
                raw_data['ad1_%s' % id_no] = ''
        with self.do_post_request('settings_telephony_am.html', raw_data) as fobj:
            fobj.read()


class GigasetPlugin(common_globals['BaseGigasetPlugin']):
    IS_PLUGIN = True
    
    _BROKER_FACTORY = GigasetRequestBroker
    
    pg_associator = common_globals['BaseGigasetPgAssociator'](MODELS)
