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

        self.assertEqual(result,
"""
[jean-yves]
amaflags = default
call-limit = 10
callerid = "lucky" <45789>
""")

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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateConfiguration']
    unittest.main()
