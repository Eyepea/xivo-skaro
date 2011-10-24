# -*- coding: UTF-8 -*-

import unittest
from xivo_ctiservers.dao.alchemy.dbconnection import DBConnection
from xivo_ctiservers.dao.alchemy.base import Base
from xivo_ctiservers.dao.alchemy.cdr import CDR
from xivo_ctiservers.dao.cdrdao import CDRDAO


class TestCDRDAO(unittest.TestCase):
    _URI = 'sqlite:///:memory:'

    def setUp(self):
        self._connection = DBConnection(self._URI)
        self._connection.connect()
        self._session = self._connection.get_session()
        self._cdrdao = CDRDAO(self._session)

        Base.metadata.create_all(self._connection.get_engine(), [CDR.__table__])

    def tearDown(self):
        Base.metadata.drop_all(self._connection.get_engine(), [CDR.__table__])

        self._connection.close()

    def _insert_cdrs(self, cdrs):
        for cdr in cdrs:
            self._session.add(cdr)
        self._session.commit()

    def test_answered_calls_for_endpoint(self):
        self._insert_cdrs([
            CDR(dstchannel=u'SIP/A-0', clid=u'1', lastapp='Dial', disposition='ANSWERED'),
            CDR(dstchannel=u'SIP/B-0', clid=u'2', lastapp='Dial', disposition='ANSWERED'),
        ])

        cdrs = self._cdrdao.answered_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual(1, len(cdrs))
        cdr = cdrs[0]
        self.assertEqual(cdr.dstchannel, u'SIP/A-0')
        self.assertEqual(cdr.clid, u'1')

    def test_missed_calls_for_endpoint(self):
        self._insert_cdrs([
            CDR(dstchannel=u'SIP/A-0', clid=u'1', lastapp='Dial', disposition='UNANSWERED'),
            CDR(dstchannel=u'SIP/B-0', clid=u'2', lastapp='Dial', disposition='UNANSWERED'),
        ])

        cdrs = self._cdrdao.missed_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual(1, len(cdrs))
        cdr = cdrs[0]
        self.assertEqual(cdr.dstchannel, u'SIP/A-0')
        self.assertEqual(cdr.clid, u'1')

    def test_outgoing_calls_for_endpoint(self):
        self._insert_cdrs([
            CDR(channel=u'SIP/A-0', dst=u'5550001'),
            CDR(channel=u'SIP/B-0', dst=u'5550002'),
        ])

        cdrs = self._cdrdao.outgoing_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual(1, len(cdrs))
        cdr = cdrs[0]
        self.assertEqual(cdr.channel, u'SIP/A-0')
        self.assertEqual(cdr.dst, u'5550001')

    def test_outgoing_calls_with_limit(self):
        self._insert_cdrs([
            CDR(channel=u'SIP/A-0', dst=u'5550001'),
            CDR(channel=u'SIP/A-0', dst=u'5550002'),
        ])

        cdrs = self._cdrdao.outgoing_calls_for_endpoint(u'SIP/A', 1)

        self.assertEqual(1, len(cdrs))
