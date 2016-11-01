import unittest
from tests.settings import connection
from asterisk import ami


class AMIClientTest(unittest.TestCase):
    client = None
    event = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)

    def build_event(self, **kwargs):
        return ami.Event('SomeEvent', kwargs)

    def test_add_event_listener(self):
        def event_listener(event, **kwargs):
            self.event = event

        self.client.add_event_listener(event_listener)
        self.client.fire_recv_event(self.build_event())
        self.assertIsNotNone(self.event)
        self.client.remove_event_listener(event_listener)
        self.assertEquals(len(self.client.listeners), 0)

        self.event = None
        listener = self.client.add_event_listener(event_listener, white_list='OtherEvent')
        self.client.fire_recv_event(self.build_event())
        self.assertIsNone(self.event)
        self.client.remove_event_listener(listener)
        self.assertEquals(len(self.client.listeners), 0)

        self.client.add_event_listener(event_listener, white_list='SomeEvent')
        self.client.fire_recv_event(self.build_event())
        self.assertIsNotNone(self.event)
