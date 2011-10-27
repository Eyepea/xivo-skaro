# -*- coding: UTF-8 -*-

class QueueStatisticEncoder(object):

    def encode(self, statistics):
        res = {}
        for queue_name, statistic in statistics.iteritems():
            res[queue_name] = {
                               'Xivo-Join': statistic.received_call_count,
                               'Xivo-Link': statistic.answered_call_count,
                               'Xivo-Lost': statistic.abandonned_call_count,
                               'Xivo-Rate' : statistic.efficiency,
                               'Xivo-Qos': statistic.qos,
                               'Xivo-Holdtime-max': statistic.max_hold_time
                               }
        return {'stats': res}
