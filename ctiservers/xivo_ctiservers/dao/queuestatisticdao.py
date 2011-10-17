from xivo_ctiservers.dao.sqlalchemy.queueinfo import QueueInfo
import time

class QueueStatisticDAO(object):

    def __init__(self):
        pass

    def get_received_call_count(self, queue_id, window):
        in_window = time.time() - window
        return (self._session.query(QueueInfo).filter(QueueInfo.queue_name == queue_id)
                .filter(QueueInfo.call_time_t > in_window).count())