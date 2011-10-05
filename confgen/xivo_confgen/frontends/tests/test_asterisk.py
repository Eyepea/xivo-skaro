'''
Created on 2011-10-05

@author: jylebleu
'''
import unittest
from xivo_confgen.frontends import asterisk
from xivo_confgen.frontends.asterisk import AsteriskFrontend
from xivo_confgen.frontend import Frontend


class Test(unittest.TestCase):
    


    def setUp(self):
        self.asteriskFrontEnd = AsteriskFrontend(None)


    def tearDown(self):
        pass


    def testGenerateDialPlanFromTemplate(self):
        template = ["%%EXTEN%%,%%PRIORITY%%,Set(XIVO_BASE_CONTEXT=${CONTEXT})"]
        exten = {}
        result = self.asteriskFrontEnd.gen_dialplan_from_template(template,exten)
        
        self.assertMultiLineEqual(result, result)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGenerateConfiguration']
    unittest.main()