import unittest
from xivo_ctiservers.model.queuestatistic import QueueStatistic
from xivo_ctiservers.statistics.queuestatisticencoder import QueueStatisticEncoder


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_encode(self):
        expected = {'service': {
               'Xivo-Join': 5,
               }}
        queuestatistic = QueueStatistic()
        queuestatistic.received_call_count = 5
        queuestatisticencoder = QueueStatisticEncoder()
        result = queuestatisticencoder.encode({'service': queuestatistic,})
        self.assertEqual(result, expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_encode']
    unittest.main()
