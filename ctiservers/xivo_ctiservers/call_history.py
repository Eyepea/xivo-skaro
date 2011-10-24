# -*- coding: UTF-8 -*-

from collections import namedtuple
from xivo_ctiservers.dao.cdrdao import CDRDAO


ReceivedCall = namedtuple('ReceivedCall', ['date', 'duration', 'caller_name'])


def _cdr_entry_to_received_call(cdr_entry):
    return ReceivedCall(cdr_entry.calldate, cdr_entry.duration, cdr_entry.clid)


SentCall = namedtuple('SentCall', ['date', 'duration', 'extension'])


def _cdr_entry_to_sent_call(cdr_entry):
    return SentCall(cdr_entry.calldate, cdr_entry.duration, cdr_entry.dst)


class CallHistoryMgr(object):
    def __init__(self, cdr_dao):
        self._cdr_dao = cdr_dao

    def answered_calls_for_endpoint(self, endpoint, limit):
        """
        endpoint -- something like "SIP/foobar"
        limit -- the number of results for the search
        """
        return [_cdr_entry_to_received_call(cdr_entry) for cdr_entry in
                self._cdr_dao.answered_calls_for_endpoint(endpoint, limit)]

    def missed_calls_for_endpoint(self, endpoint, limit):
        return [_cdr_entry_to_received_call(cdr_entry) for cdr_entry in
                self._cdr_dao.missed_calls_for_endpoint(endpoint, limit)]

    def outgoing_calls_for_endpoint(self, endpoint, limit):
        return [_cdr_entry_to_sent_call(cdr_entry) for cdr_entry in
                self._cdr_dao.outgoing_calls_for_endpoint(endpoint, limit)]

    @classmethod
    def new_from_uri(cls, uri):
        return cls(CDRDAO.new_from_uri(uri))
