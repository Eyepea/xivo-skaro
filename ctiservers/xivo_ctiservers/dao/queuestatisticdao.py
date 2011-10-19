import time

from xivo_ctiservers.dao.sqlalchemy.queueinfo import QueueInfo
from xivo_ctiservers.dao.sqlalchemy.dbconnection import DBConnection

class QueueStatisticDAO(object):

    def __init__(self):
        pass

    def get_received_call_count(self, queue_id, window):
        in_window = time.time() - window
        return (DBConnection.getSession().query(QueueInfo).filter(QueueInfo.queue_name == queue_id)
                .filter(QueueInfo.call_time_t > in_window).count())

