
import unittest
from xivo_ctiservers.statistics.queuestatisticmanager import QueueStatisticManager
from tests.mock import Mock
from xivo_ctiservers.dao.queuestatisticdao import QueueStatisticDAO



class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_getStatistics(self):
        queue_statistic_dao = Mock(QueueStatisticDAO)
        queue_statistic_manager = QueueStatisticManager()
        window = 3600
        xqos = 25
        queue_statistic_manager._queue_statistic_dao = queue_statistic_dao
        queue_statistic_dao.get_received_call_count.return_value = 7
        queue_statistic_dao.get_answered_call_count.return_value = 12
        
        
        queue_statistics = queue_statistic_manager.get_statistics('3', xqos, window)
        
        
        self.assertEqual(queue_statistics.received_call_count, 7)
        self.assertEqual(queue_statistics.answered_call_count, 12)
        queue_statistic_dao.get_received_call_count.assert_called_with('3', window)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()