# -*- coding: UTF-8 -*-

import unittest
import sys

from xivo_confgen.frontends.asterisk import AsteriskFrontend


class Test(unittest.TestCase):


    def setUp(self):
        self.asteriskFrontEnd = AsteriskFrontend(None)

    def tearDown(self):
        pass

# é oh è
    def testGenerateDialPlanFromTemplate(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set(XIVO_BASE_CONTEXT=${CONTEXT})"]
        exten = {'exten':'*98', 'priority':1}
        result = self.asteriskFrontEnd.gen_dialplan_from_template(template, exten)

        self.assertEqual(result, "exten = *98,1,Set(XIVO_BASE_CONTEXT=${CONTEXT})\n")

    def testGenSipUser(self):
        user = {'name':'jean-yves',
                'amaflags': 'default',
                'callerid': '"lucky" <45789>',
                'call-limit':10}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        
        #caller_id = set(['callerid = "lucky" <45789>'])
        #set_result = set(result.split('\n'))
#        self.assertTrue(caller_id in set_result)
        self.assertEqual(result, 
"""
[jean-yves]
amaflags = default
call-limit = 10
callerid = "lucky" <45789>
""")
        
    def testGenSipUserWithAccent(self):
        user = {'name':'papi',
                u'callerid': u'"pépè" <45789>'}
        pickups = {}
        result = self.asteriskFrontEnd.gen_sip_user(user, pickups)
        self.assertEqual(result,u'\n[papi]\ncallerid = "pépè" <45789>\n') 
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateConfiguration']
    unittest.main()
