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

    def test_regcommand_featuresput(self):
        from xivo_ctiservers import cti_command
        xws_inst = Mock()
        xws_inst.connect    = Mock()
        xws_inst.serviceput = Mock()
        xws = Mock()
        xws.__init__(return_value=xws_inst)
        cti_command.xivo_webservices.xws = xws

        conn = Mock()
        conn.requester = ('test_requester', 3)

        ##
        message = {'class': 'featuresput',
            'commandid': 1235,
            'function': 'callrecord',
            'value': True}

        ## 1. invalid/unknown user
        cmd = Command(conn, message)
        cmd.ruserid = -1
        cmd.rinnerdata = Mock()

        m_users = Mock()
        m_users.finduser = Mock(return_value=None)
        cmd.rinnerdata.xod_config = {'users':m_users}
        res = cmd.regcommand_featuresput()

        self.assertFalse(xws_inst.serviceput.called)
        self.assertEqual(res, {'status':'KO','error_string': 'unknown -1 user'})

        ## 2. value not changed
        cmd = Command(conn, message)
        cmd.ruserid = 1
        cmd.rinnerdata = Mock()

        user    = Mock()
        user.get = Mock(return_value=True)
        m_users = Mock()
        m_users.finduser = Mock(return_value=user)
        cmd.rinnerdata.xod_config = {'users':m_users}
        res = cmd.regcommand_featuresput()

        self.assertFalse(xws_inst.serviceput.called)
        self.assertEqual(res, {'status':'OK','warning_string': 'no changes'})

        ## 3. ok (simple feature)
        cmd = Command(conn, message)
        cmd.ruserid = 1
        cmd.rinnerdata = Mock()
        res = cmd.regcommand_featuresput()

        self.assertEqual(res['status'],'OK')
        self.assertTrue(xws_inst.connect.called)
        xws_inst.serviceput.assert_called_with(1, {'callrecord': True})
        xws.inst.connect.reset_mock()
        xws_inst.serviceput.reset_mock()

        ## 4. ok (feature with value)
        message = {'class': 'featuresput',
            'commandid': 1522263052,
            'function': 'fwd',
            'value': {'destrna': '123', 'enablerna': True}
        }

        cmd = Command(conn, message)
        cmd.ruserid = 1
        cmd.rinnerdata = Mock()
        cmd.regcommand_featuresput()

        self.assertEqual(res['status'],'OK')
        self.assertTrue(xws_inst.connect.called)
        xws_inst.serviceput.assert_called_with(1, {'enablerna': True, 'destrna': '123'})


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

