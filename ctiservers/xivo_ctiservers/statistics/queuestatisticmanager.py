# -*- coding: UTF-8 -*-
from xivo_ctiservers.dao.queuestatisticdao import QueueStatisticDAO
from xivo_ctiservers.model.queuestatistic import QueueStatistic

class QueueStatisticManager(object):

    def __init__(self):
        self._queue_statistic_dao = QueueStatisticDAO()

    def get_statistics(self, queue_name, xqos, window):
        queue_statistic = QueueStatistic()
        queue_statistic.received_call_count = self._queue_statistic_dao.get_received_call_count(queue_name, window)
        queue_statistic.answered_call_count = self._queue_statistic_dao.get_answered_call_count(queue_name, window)
        queue_statistic.abandonned_call_count = self._queue_statistic_dao.get_abandonned_call_count(queue_name, window)
        return queue_statistic
