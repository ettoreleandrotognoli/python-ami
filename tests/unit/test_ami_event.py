import unittest
from asterisk import ami


class AMIEventTest(unittest.TestCase):
    def test_dict(self):
        keys = {'a': 1, 'b': 2}
        event = ami.Event('TestEvent', dict(keys))
        self.assertEquals(event['a'], 1)
        self.assertEquals(event['b'], 2)
        self.assertListEqual(list(iter(keys)), list(iter(event)))
