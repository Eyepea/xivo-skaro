# -*- coding: UTF-8 -*-

class QueueStatistic(object):


    def __init__(self):
        self.received_call_count = 0
        self.answered_call_count = 0
        self.abandonned_call_count = 0
        self.max_hold_time = 0
        self.efficiency = None
        self.qos = None
