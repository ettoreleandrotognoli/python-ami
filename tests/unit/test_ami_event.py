import unittest
from asterisk import ami


class AMIEventTest(unittest.TestCase):
    def test_dict(self):
        keys = {'a': 1, 'b': 2}
        event = ami.Event('TestEvent', dict(keys))
        self.assertEqual(event['a'], 1)
        self.assertEqual(event['b'], 2)
        self.assertListEqual(list(iter(keys)), list(iter(event)))
        self.assertIn('a', event)
