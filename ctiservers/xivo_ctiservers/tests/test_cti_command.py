# -*- coding: UTF-8 -*-

import unittest
from tests.mock import Mock
from xivo_ctiservers.cti_command import Command
from xivo_ctiservers.statistics.queuestatisticmanager import QueueStatisticManager
from xivo_ctiservers.statistics.queuestatisticencoder import QueueStatisticEncoder
from xivo_ctiservers.innerdata import Safe
from xivo_ctiservers.lists.cti_queuelist import QueueList


class Test(unittest.TestCase):


    def setUp(self):
        self.conn = Mock()
        self.conn.requester = ('test_requester', 1)


    def tearDown(self):
        pass

    def test_regcommand_getqueuesstats_no_result(self):
        message = {}
        cti_command = Command(self.conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')

    def test_regcommand_getqueuesstats_one_queue(self):
        queueList = Mock(QueueList)
        queueList.keeplist ={'3':{'name':'service'}}
        safe = Mock(Safe)
        safe.xod_config = {'queues':queueList}

        message = {"class": "getqueuesstats",
                   "commandid": 1234,
                   "on": {"3": {"window": "3600", "xqos": "60"}}}
        queueStatistics = Mock(QueueStatisticManager)
        encoder = Mock(QueueStatisticEncoder)
        cti_command = Command(self.conn, message)
        cti_command.innerdata = safe
        cti_command._queue_statistic_manager = queueStatistics
        cti_command._queue_statistic_encoder = encoder

        queueStatistics.get_statistics.return_value = queueStatistics
        statisticsToEncode = {'3': queueStatistics}

        encoder.encode.return_value = {'return value': {'value1': 'first stat'}}

        reply = cti_command.regcommand_getqueuesstats()
        self.assertEqual(reply, {'return value': {'value1': 'first stat'}})

        queueStatistics.get_statistics.assert_called_with('service', 60, 3600)
        encoder.encode.assert_called_with(statisticsToEncode)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
