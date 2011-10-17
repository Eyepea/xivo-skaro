
import unittest
from tests.mock import Mock
from xivo_ctiservers.cti_command import Command
from xivo_ctiservers.statistics.queuestatisticmanager import QueueStatisticManager


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def test_regcommand_getqueuesstats_no_result(self):
        conn = Mock()
        conn.requester = ('test_requester', 1)
        message = {}
        cti_command = Command(conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')

    def test_regcommand_getqueuesstats_one_queue(self):
        conn = Mock()
        conn.requester = ('test_requester', 2)
        message = {"class": "getqueuesstats",
                   "commandid": 1234,
                   "on": {"3": {"window": "3600", "xqos": "60"}}}
        queueStatistics = Mock(QueueStatisticManager)
        cti_command = Command(conn, message)
        cti_command._queue_statistics_manager = queueStatistics

        cti_command.regcommand_getqueuesstats()

        queueStatistics.get_statistics.assert_called_with('3', 60, 3600)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()