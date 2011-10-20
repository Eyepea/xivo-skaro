
import unittest
from xivo_ctiservers.statistics.queuestatisticmanager import QueueStatisticManager
from tests.mock import Mock
from xivo_ctiservers.dao.queuestatisticdao import QueueStatisticDAO



class Test(unittest.TestCase):

    def setUp(self):
        self.queue_statistic_dao = Mock(QueueStatisticDAO)
        self.queue_statistic_manager = QueueStatisticManager()
        self.queue_statistic_manager._queue_statistic_dao = self.queue_statistic_dao
        

    def tearDown(self):
        pass

    def test_getStatistics(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 7
        self.queue_statistic_dao.get_answered_call_count.return_value = 12
        self.queue_statistic_dao.get_abandonned_call_count.return_value = 11
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 11
        self.queue_statistic_dao.get_max_hold_time.return_value = 120

        queue_statistics = self.queue_statistic_manager.get_statistics('3', xqos, window)


        self.assertEqual(queue_statistics.received_call_count, 7)
        self.assertEqual(queue_statistics.answered_call_count, 12)
        self.assertEqual(queue_statistics.abandonned_call_count, 11)
        self.assertEqual(queue_statistics.max_hold_time, 120)
        self.queue_statistic_dao.get_received_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_answered_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_abandonned_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_max_hold_time.assert_called_with('3', window)

    def test_calculate_efficiency(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 18
        self.queue_statistic_dao.get_answered_call_count.return_value = 3
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 11


        queue_statistics = self.queue_statistic_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, 27)


    def test_efficiency_no_call_received_and_done(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 3
        self.queue_statistic_dao.get_answered_call_count.return_value = 0
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 0

        queue_statistics = self.queue_statistic_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, None)

    def test_qos(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_answered_call_count.return_value = 11
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 3
        self.queue_statistic_dao.get_received_call_count.return_value = 50
        self.queue_statistic_dao.get_received_and_done.return_value = 11

        queue_statistics = self.queue_statistic_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.qos, 27)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()