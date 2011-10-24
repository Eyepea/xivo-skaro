# -*- coding: UTF-8 -*-

import datetime
import unittest
from tests.mock import Mock
from xivo_ctiservers.call_history import CallHistoryMgr, ReceivedCall, SentCall
from xivo_ctiservers.dao.alchemy.cdr import CDR


class CallHistoryMgrTest(unittest.TestCase):
    def test_answered_calls_for_endpoint(self):
        cdr_dao = Mock()
        date = datetime.datetime.now()
        duration = 1
        caller_name = u'Foo'
        cdr_dao.answered_calls_for_endpoint.return_value = [
            CDR(calldate=date, duration=duration, clid=caller_name)
        ]

        call_history_mgr = CallHistoryMgr(cdr_dao)
        received_calls = call_history_mgr.answered_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([ReceivedCall(date, duration, caller_name)], received_calls)

    def test_missed_calls_for_endpoint(self):
        cdr_dao = Mock()
        date = datetime.datetime.now()
        duration = 1
        caller_name = u'Foo'
        cdr_dao.missed_calls_for_endpoint.return_value = [
            CDR(calldate=date, duration=duration, clid=caller_name)
        ]

        call_history_mgr = CallHistoryMgr(cdr_dao)
        received_calls = call_history_mgr.missed_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([ReceivedCall(date, duration, caller_name)], received_calls)

    def test_outgoing_calls_for_endpoint(self):
        cdr_dao = Mock()
        date = datetime.datetime.now()
        duration = 1
        extension = u'Foo'
        cdr_dao.outgoing_calls_for_endpoint.return_value = [
            CDR(calldate=date, duration=duration, dst=extension)
        ]

        call_history_mgr = CallHistoryMgr(cdr_dao)
        sent_calls = call_history_mgr.outgoing_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([SentCall(date, duration, extension)], sent_calls)
