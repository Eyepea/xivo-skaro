'''
Created on 2011-10-05

@author: jylebleu
'''
import unittest
from xivo_confgen.frontends.asterisk import AsteriskFrontend


class Test(unittest.TestCase):
    


    def setUp(self):
        self.asteriskFrontEnd = AsteriskFrontend(None)


    def tearDown(self):
        pass


    def testGenerateDialPlanFromTemplate(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set(XIVO_BASE_CONTEXT=${CONTEXT})"]
        exten = {'exten':'*98','priority':1}
        result = self.asteriskFrontEnd.gen_dialplan_from_template(template,exten)
        
        self.assertEqual(result, "exten = *98,1,Set(XIVO_BASE_CONTEXT=${CONTEXT})\n")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateConfiguration']
    unittest.main()