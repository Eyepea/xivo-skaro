import time

from xivo_ctiservers.dao.sqlalchemy.queueinfo import QueueInfo
from xivo_ctiservers.dao.sqlalchemy.dbconnection import DBConnection


class QueueStatisticDAO(object):

    def __init__(self):
        pass

    def get_received_call_count(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (DBConnection.getSession().query(QueueInfo).filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window).count())

    def get_answered_call_count(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (DBConnection.getSession().query(QueueInfo).filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window).filter(QueueInfo.call_picker != '').count())

    def _compute_window_time(self, window):
        return time.time() - window
