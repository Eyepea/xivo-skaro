import unittest
from xivo_ctiservers.model.queuestatistic import QueueStatistic
from xivo_ctiservers.statistics.queuestatisticencoder import QueueStatisticEncoder


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_encode(self):
        '''
         13:54:50.718095 Client > Server
           {"class": "getqueuesstats", "on": {"2": {"window": "3600", "xqos": "60"}, "3": {"window": "3600", "xqos": "60"}}}
        13:54:50.752110 Server > Client
        {"class": "queuestats", "direction": "client", "function": "update", "stats": {"2": {"Xivo-Holdtime-avg": "na", "Xivo-Holdtime-max": "na", "Xivo-Join": "0", "Xivo-Link": "0", "Xivo-Lost": "0", "Xivo-Qos": "na", "Xivo-Rate": "na", "Xivo-TalkingTime": "na"}, "3": {"Xivo-Holdtime-avg": "na", "Xivo-Holdtime-max": "na", "Xivo-Join": "0", "Xivo-Link": "0", "Xivo-Lost": "0", "Xivo-Qos": "na", "Xivo-Rate": "na", "Xivo-TalkingTime": "na"}}, "timenow": 1318960490.74}
        '''
        expected = {'stats': {'3': {
                                          'Xivo-Join': 5,
                                          }}}
        queuestatistic = QueueStatistic()
        queuestatistic.received_call_count = 5
        queuestatisticencoder = QueueStatisticEncoder()
        statistic_results = {}
        statistic_results['3'] = queuestatistic
        result = queuestatisticencoder.encode(statistic_results)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_encode']
    unittest.main()
