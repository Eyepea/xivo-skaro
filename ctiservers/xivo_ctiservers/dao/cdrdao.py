# -*- coding: UTF-8 -*-

from sqlalchemy import or_
from xivo_ctiservers.dao.alchemy.cdr import CDR
from xivo_ctiservers.dao.alchemy import dbconnection


class CDRDAO(object):
    def __init__(self, session):
        self._session = session

    def _new_query(self):
        return self._session.query(CDR).order_by(CDR.calldate.desc())

    def _channel_pattern_from_endpoint(self, endpoint):
        return "%s-%%" % endpoint

    def answered_calls_for_endpoint(self, endpoint, limit):
        query = self._new_query()
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        return (query
                .filter(CDR.disposition == "ANSWERED")
                .filter(CDR.lastapp == "Dial")
                .filter(CDR.dstchannel.like(channel_pattern))
                .limit(limit)
                .all())

    def missed_calls_for_endpoint(self, endpoint, limit):
        query = self._new_query()
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        return (query
                .filter(or_(CDR.disposition != "ANSWERED", CDR.lastapp != "Dial"))
                .filter(CDR.dstchannel.like(channel_pattern))
                .limit(limit)
                .all())

    def outgoing_calls_for_endpoint(self, endpoint, limit):
        query = self._new_query()
        channel_pattern = self._channel_pattern_from_endpoint(endpoint)
        return (query
                .filter(CDR.channel.like(channel_pattern))
                .limit(limit)
                .all())

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
