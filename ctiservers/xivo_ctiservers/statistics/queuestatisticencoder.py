# -*- coding: UTF-8 -*-

class QueueStatisticEncoder(object):
    
    def encode(self, statistics):
        res = {}
        for queue_name, statistic in statistics.iteritems():
            res[queue_name] = {
                               'Xivo-Join': statistic.received_call_count,
                               }
        return res
