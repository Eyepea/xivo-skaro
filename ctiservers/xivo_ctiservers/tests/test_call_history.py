# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime
from tests.mock import Mock
from xivo_ctiservers.call_history import CallHistoryMgr, ReceivedCall, SentCall


class CallHistoryMgrTest(unittest.TestCase):
    def test_answered_calls_for_endpoint(self):
        date = datetime.now()
        duration = 1
        caller_name = u'"Foo" <123>'

        cel_channel = Mock()
        cel_channel.linked_id.return_value = '1'
        cel_channel.channel_start_time.return_value = date
        cel_channel.answer_duration.return_value = duration

        cel_dao = Mock()
        cel_dao.answered_channels_for_endpoint.return_value = [
            cel_channel
        ]
        cel_dao.caller_id_by_unique_id.return_value = caller_name

        call_history_mgr = CallHistoryMgr(cel_dao)
        received_calls = call_history_mgr.answered_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([ReceivedCall(date, duration, caller_name)], received_calls)

    def test_missed_calls_for_endpoint(self):
        date = datetime.now()
        caller_name = u'"Foo" <123>'

        cel_channel = Mock()
        cel_channel.linked_id.return_value = '1'
        cel_channel.channel_start_time.return_value = date

        cel_dao = Mock()
        cel_dao.missed_channels_for_endpoint.return_value = [
            cel_channel
        ]
        cel_dao.caller_id_by_unique_id.return_value = caller_name

        call_history_mgr = CallHistoryMgr(cel_dao)
        received_calls = call_history_mgr.missed_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([ReceivedCall(date, 0.0, caller_name)], received_calls)

    def test_outgoing_calls_for_endpoint(self):
        date = datetime.now()
        duration = 1
        extension = u'100'

        cel_channel = Mock()
        cel_channel.channel_start_time.return_value = date
        cel_channel.answer_duration.return_value = duration
        cel_channel.exten.return_value = extension

        cel_dao = Mock()
        cel_dao.outgoing_channels_for_endpoint.return_value = [
            cel_channel
        ]

        call_history_mgr = CallHistoryMgr(cel_dao)
        sent_calls = call_history_mgr.outgoing_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([SentCall(date, duration, extension)], sent_calls)
