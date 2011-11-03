# -*- coding: UTF-8 -*-

from collections import namedtuple
from xivo_ctiservers.dao.celdao import CELDAO


ReceivedCall = namedtuple('ReceivedCall', ['date', 'duration', 'caller_name'])


SentCall = namedtuple('SentCall', ['date', 'duration', 'extension'])


class CallHistoryMgr(object):
    def __init__(self, cel_dao):
        self._cel_dao = cel_dao

    def answered_calls_for_endpoint(self, endpoint, limit):
        """
        endpoint -- something like "SIP/foobar"
        """
        answered_channels = self._cel_dao.answered_channels_for_endpoint(endpoint, limit)
        received_calls = []
        for answered_channel in answered_channels:
            caller_id = self._cel_dao.caller_id_by_unique_id(answered_channel.linked_id())
            received_call = ReceivedCall(answered_channel.channel_start_time(),
                                         answered_channel.answer_duration(),
                                         caller_id)
            received_calls.append(received_call)
        return received_calls

    def missed_calls_for_endpoint(self, endpoint, limit):
        missed_channels = self._cel_dao.missed_channels_for_endpoint(endpoint, limit)
        received_calls = []
        for missed_channel in missed_channels:
            caller_id = self._cel_dao.caller_id_by_unique_id(missed_channel.linked_id())
            received_call = ReceivedCall(missed_channel.channel_start_time(),
                                         0.0,
                                         caller_id)
            received_calls.append(received_call)
        return received_calls

    def outgoing_calls_for_endpoint(self, endpoint, limit):
        outgoing_channels = self._cel_dao.outgoing_channels_for_endpoint(endpoint, limit)
        sent_calls = []
        for outgoing_channel in outgoing_channels:
            sent_call = SentCall(outgoing_channel.channel_start_time(),
                                 outgoing_channel.answer_duration(),
                                 outgoing_channel.exten())
            sent_calls.append(sent_call)
        return sent_calls

    @classmethod
    def new_from_uri(cls, uri):
        return cls(CELDAO.new_from_uri(uri))
