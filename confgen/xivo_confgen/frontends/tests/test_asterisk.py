# -*- coding: UTF-8 -*-

import unittest
import sys

from xivo_confgen.frontends.asterisk import AsteriskFrontend


class Test(unittest.TestCase):
    def setUp(self):
        self.asteriskFrontEnd = AsteriskFrontend(None)

    def tearDown(self):
        pass

    def test_encoding(self):
        charset = ("ascii", "US-ASCII",)
        self.assertTrue(sys.getdefaultencoding() in charset, "Test should be run in ascii")

    def test_get_line(self):
        result = self.asteriskFrontEnd._gen_value_line('emailbody', 'pépè')
        self.assertEqual(result, u'emailbody = pépè')

    def test_unicodify_string(self):
            self.assertEqual(u'pépé',
                             self.asteriskFrontEnd._unicodify_string(u'pépé'))
            self.assertEqual(u'pépé',
                             self.asteriskFrontEnd._unicodify_string(u'pépé'.encode('utf8')))
            self.assertEqual(u'pépé', self.asteriskFrontEnd._unicodify_string('pépé'))
            self.assertEqual(u'8', self.asteriskFrontEnd._unicodify_string(8))

    def test_get_not_none(self):
        d = {'one': u'pépè',
             'two': u'pépè'.encode('utf8'),
             'three': None}
        self.assertEqual(u'pépè', self.asteriskFrontEnd._get_is_not_none(d, 'one'))
        self.assertEqual(u'pépè', self.asteriskFrontEnd._get_is_not_none(d, 'two'))
        self.assertEqual(u'', self.asteriskFrontEnd._get_is_not_none(d, 'three'))

    def test_generate_dialplan_from_template(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set(XIVO_BASE_CONTEXT=${CONTEXT})"]
        exten = {'exten':'*98', 'priority':1}
        result = self.asteriskFrontEnd.gen_dialplan_from_template(template, exten)

        self.assertEqual(result, "exten = *98,1,Set(XIVO_BASE_CONTEXT=${CONTEXT})\n")

    def test_gen_sip_user(self):
        user = {'name':'jean-yves',
                'amaflags': 'default',
                'callerid': '"lucky" <45789>',
                'call-limit':10}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertTrue(u'[jean-yves]' in result)
        self.assertTrue(u'amaflags = default' in result)
        self.assertTrue(u'call-limit = 10' in result)
        self.assertTrue(u'callerid = "lucky" <45789>' in result)

    def test_gen_sip_user_with_accent(self):
        user = {'name':'papi',
                u'callerid': u'"pépè" <45789>'}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[papi]\ncallerid = "pépè" <45789>\n')

    def test_gen_sip_user_empty_value(self):
        user = {'name':'novalue',
                u'context': u''}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[novalue]\n')

        user = {'name':'novalue',
                u'context': None}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[novalue]\n')

    def test_gen_sip_user_codec(self):
        user = {'name':'papi',
                u'allow': u'g723,gsm'}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[papi]\ndisallow = all\nallow = g723\nallow = gsm\n')

    def test_gen_sip_user_subscribemwi(self):
        user = {'name':'voicemail',
                u'subscribemwi': 0}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[voicemail]\nsubscribemwi = no\n')
        user = {'name':'voicemail',
                u'subscribemwi': 1}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[voicemail]\nsubscribemwi = yes\n')

    def test_gen_sip_user_unused_keys(self):
        user = {'id': 1,
                'name': 'unused',
                'protocol': 'sip',
                'category': 5,
                'commented': 0,
                'initialized': 1,
                'disallow': 'all',
                'regseconds': 1,
                'lastms': 5,
                'fullcontact': 'pepe',
                'ipaddr': None, }
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result, u'\n[unused]\n')

    def test_voicemail_conf_gen_emailbody_accents(self):
        general_config = {'var_name': 'emailbody',
                          'var_val': 'pépè'}
        result = self.asteriskFrontEnd._gen_voicemail_emailbody(general_config)
        self.assertEqual(result, u'emailbody = pépè\n')

    def test_voicemail_conf_gen_emailbody_empty(self):
        general_config = {}
        result = self.asteriskFrontEnd._gen_voicemail_emailbody(general_config)
        self.assertEqual(result, '')

    def test_voicemail_conf_gen_context_accents(self):
        voicemail_context = {'context': 'default',
                             'mailbox': 8000,
                             'password': 'password',
                             'fullname': 'cédric',
                             'email': 'dev@avencall.com',
                             'pager': 'pager',
                             'imapuser': None}
        self.asteriskFrontEnd._vm_context = None
        result = self.asteriskFrontEnd._gen_voicemail_context(voicemail_context)
        self.assertTrue(u'[default]' in result)
        self.assertTrue(u'8000 => password,cédric,dev@avencall.com,pager,' in result)

    def test_voicemail_conf_gen_imapusers(self):
        self.asteriskFrontEnd._imapusers = [{'uniqueid': 1, 'context': u'default',
                                             'mailbox': u'8000', 'password': u'0000',
                                             'fullname': u'cédric', 'email': None,
                                             'pager': None, 'dialout': None, 'callback': None,
                                             'exitcontext': None, 'language': None,
                                             'tz': u'eu-fr', 'attach': None, 'saycid': None,
                                             'review': None, 'operator': None, 'envelope': None,
                                             'sayduration': None, 'saydurationm': None,
                                             'sendvoicemail': None, 'deletevoicemail': 0,
                                             'forcename': None, 'forcegreetings': None,
                                             'hidefromdir': u'no', 'maxmsg': None,
                                             'emailsubject': u'éééé', 'emailbody': u'test',
                                             'imapuser': u'cabunar', 'imappassword': u'superpass',
                                             'imapfolder': u'lol', 'imapvmsharedid': u'lol',
                                             'attachfmt': None, 'serveremail': u'francis',
                                             'locale': u'fr_FR', 'tempgreetwarn': None,
                                             'messagewrap': None, 'moveheard': None,
                                             'minsecs': None, 'maxsecs': None, 'nextaftercmd': None,
                                             'backupdeleted': None, 'volgain': None,
                                             'passwordlocation': None, 'commented': 0}]
        result = self.asteriskFrontEnd._gen_voicemail_imapusers()
        self.assertTrue(u'[imapvm]' in result)
        self.assertTrue(u'8000 => 0000,cédric,,,imappassword = superpass|imapfolder = lol|imapuser = cabunar' in result)

    def test_iax_conf_gen_trunk(self):
        trunk = {'id': 1, 'name': u'xivo_devel_51', 'type': u'friend', 'username': u'xivo_devel_51',
                  'secret': u'xivo_devel_51', 'dbsecret': u'', 'context': u'default', 'language': u'fr_FR',
                  'accountcode': None, 'amaflags': None, 'mailbox': None, 'callerid': None, 'fullname': None,
                  'cid_number': None, 'trunk': 0, 'auth': u'plaintext,md5', 'encryption': None,
                  'forceencryption': None, 'maxauthreq': None, 'inkeys': None, 'outkey': None, 'adsi': None,
                  'transfer': None, 'codecpriority': None, 'jitterbuffer': None, 'forcejitterbuffer': None,
                  'sendani': 0, 'qualify': u'no', 'qualifysmoothing': 0, 'qualifyfreqok': 60000,
                  'qualifyfreqnotok': 10000, 'timezone': None, 'disallow': None, 'allow': None,
                  'mohinterpret': None, 'mohsuggest': None, 'deny': None, 'permit': None, 'defaultip': None,
                  'sourceaddress': None, 'setvar': u'', 'host': u'192.168.32.253', 'port': 4569, 'mask': None,
                  'regexten': None, 'peercontext': None, 'ipaddr': u'', 'regseconds': 0, 'immediate': None,
                  'parkinglot': None, 'protocol': u'iax', 'category': u'trunk', 'commented': 0,
                  'requirecalltoken': u'auto'}
        result = self.asteriskFrontEnd._gen_iax_trunk(trunk)
        self.assertTrue(u'[xivo_devel_51]' in result)
        self.assertTrue(u'regseconds =  0' in result)
        self.assertTrue(u'qualifysmoothing =  0' in result)
        self.assertTrue(u'secret =  xivo_devel_51' in result)
        self.assertTrue(u'type =  friend' in result)
        self.assertTrue(u'username =  xivo_devel_51' in result)
        self.assertTrue(u'auth =  plaintext,md5' in result)
        self.assertTrue(u'qualifyfreqnotok =  10000' in result)
        self.assertTrue(u'requirecalltoken =  auto' in result)
        self.assertTrue(u'port =  4569' in result)
        self.assertTrue(u'context =  default' in result)
        self.assertTrue(u'sendani =  0' in result)
        self.assertTrue(u'qualify =  no' in result)
        self.assertTrue(u'trunk =  0' in result)
        self.assertTrue(u'language =  fr_FR' in result)
        self.assertTrue(u'host =  192.168.32.253' in result)
        self.assertTrue(u'qualifyfreqok =  60000' in result)

    def test_iax_conf_gen_general(self):
        staticiax = [{'filename': u'iax.conf', 'category': u'general', 'var_name': u'bindport', 'var_val': u'4569'},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'bindaddr', 'var_val': u'0.0.0.0'},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'iaxcompat', 'var_val': u'no'},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'authdebug', 'var_val': u'yes'},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'srvlookup', 'var_val': None},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'shrinkcallerid', 'var_val': None},
                    {'filename': u'iax.conf', 'category': u'general', 'var_name': u'language', 'var_val': u'fr_FR'}]
        result = self.asteriskFrontEnd._gen_iax_general(staticiax)
        self.assertTrue(u'[general]' in result)
        self.assertTrue(u'bindport = 4569' in result)
        self.assertTrue(u'bindaddr = 0.0.0.0' in result)
        self.assertTrue(u'iaxcompat = no' in result)
        self.assertTrue(u'authdebug = yes' in result)
        self.assertTrue(u'language = fr_FR' in result)

    def test_iax_conf_gen_users(self):
        useriax = [{'id': 2, 'name': u'6rh29c', 'type': u'friend', 'username': None, 'secret': u'DC8HTI',
                    'dbsecret': u'', 'context': u'default', 'language': None, 'accountcode': None,
                    'amaflags': None, 'mailbox': None, 'callerid': u'"hq"', 'fullname': None,
                    'cid_number': None, 'trunk': 0, 'auth': u'plaintext,md5', 'encryption': None,
                    'forceencryption': None, 'maxauthreq': None, 'inkeys': None, 'outkey': None,
                    'adsi': None, 'transfer': None, 'codecpriority': None, 'jitterbuffer': None,
                    'forcejitterbuffer': None, 'sendani': 0, 'qualify': u'no', 'qualifysmoothing': 0,
                    'qualifyfreqok': 60000, 'qualifyfreqnotok': 10000, 'timezone': None, 'disallow': None,
                    'allow': None, 'mohinterpret': None, 'mohsuggest': u'default', 'deny': None,
                    'permit': None, 'defaultip': None, 'sourceaddress': None, 'setvar': u'',
                    'host': u'dynamic', 'port': None, 'mask': None, 'regexten': None, 'peercontext': None,
                    'ipaddr': u'', 'regseconds': 0, 'immediate': None, 'parkinglot': None, 'protocol': u'iax',
                    'category': u'user', 'commented': 0, 'requirecalltoken': u''}]
        result = self.asteriskFrontEnd._gen_iax_users(useriax)
        self.assertTrue(u'[6rh29c]' in result)
        self.assertTrue(u'regseconds = 0' in result)
        self.assertTrue(u'callerid = "hq"' in result)
        self.assertTrue(u'qualifysmoothing = 0' in result)
        self.assertTrue(u'secret = DC8HTI' in result)
        self.assertTrue(u'type = friend' in result)
        self.assertTrue(u'auth = plaintext,md5' in result)
        self.assertTrue(u'qualifyfreqnotok = 10000' in result)
        self.assertTrue(u'mohsuggest = default' in result)
        self.assertTrue(u'context = default' in result)
        self.assertTrue(u'sendani = 0' in result)
        self.assertTrue(u'qualify = no' in result)
        self.assertTrue(u'trunk = 0' in result)
        self.assertTrue(u'host = dynamic' in result)
        self.assertTrue(u'qualifyfreqok = 60000' in result)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateConfiguration']
    unittest.main()
