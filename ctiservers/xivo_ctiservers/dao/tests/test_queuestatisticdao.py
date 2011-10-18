
import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from xivo_ctiservers.dao.sqlalchemy.queueinfo import QueueInfo
from xivo_ctiservers.dao.sqlalchemy.base import Base
import time
from xivo_ctiservers.dao.queuestatisticdao import QueueStatisticDAO
from xivo_ctiservers.dao.sqlalchemy.dbconnection import DBConnection


class Test(unittest.TestCase):


    def setUp(self):
        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        connection = DBConnection(uri)
        connection.connect()

        Base.metadata.drop_all(connection.getEngine(), [QueueInfo().__table__])
        Base.metadata.create_all(connection.getEngine(), [QueueInfo().__table__])

        self.session = connection.getSession()

        self.session.commit()
        self._queue_statistic_dao = QueueStatisticDAO()
        self._queue_statistic_dao._session = self.session

    def tearDown(self):
        pass

    def _insert_received_calls(self, window, nb_in_window):
        out_of_window_delta = window + 30
        in_window = time.time()
        count_out_window = 3
        queuename = 'service'
        out_of_window = time.time() - out_of_window_delta
        for i in range(nb_in_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = in_window
            queueinfo.queue_name = queuename
            self.session.add(queueinfo)
        for i in range(count_out_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = out_of_window
            queueinfo.queue_name = queuename
            self.session.add(queueinfo)
        self.session.commit()

    def test_get_received_call(self):
        window = 3600 # one hour
        count_in_window = 5
        self._insert_received_calls(window, count_in_window)
        number_of_received_calls = self._queue_statistic_dao.get_received_call_count('service', window)
        self.assertEqual(number_of_received_calls, count_in_window)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()