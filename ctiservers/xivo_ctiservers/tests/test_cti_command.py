
import unittest
from tests.mock import Mock
from xivo_ctiservers.cti_command import Command


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def test_regcommand_getqueuesstats(self):
        conn = Mock()
        conn.requester = ('test_requester', 1)
        message = {}
        cti_command = Command(conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()