import unittest
from tests.settings import connection
from asterisk import ami


class AMIClientTest(unittest.TestCase):
    client = None
    event = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)

    def build_event(self, event='SomeEvent', **kwargs):
        return ami.Event(event, kwargs)

    def test_add_event_listener(self):
        def event_listener(event, **kwargs):
            self.event = event

        self.client.add_event_listener(event_listener)
        self.client.fire_recv_event(self.build_event())
        self.assertIsNotNone(self.event)
        self.client.remove_event_listener(event_listener)
        self.assertEqual(len(self.client._event_listeners), 0)

        self.event = None
        listener = self.client.add_event_listener(event_listener, white_list='OtherEvent')
        self.client.fire_recv_event(self.build_event())
        self.assertIsNone(self.event)
        self.client.remove_event_listener(listener)
        self.assertEqual(len(self.client._event_listeners), 0)

        self.client.add_event_listener(event_listener, white_list='SomeEvent')
        self.client.fire_recv_event(self.build_event())
        self.assertIsNotNone(self.event)

    registry_event = None
    varset_event = None

    def test_add_custom_on_event(self):
        def on_varset(event, **kwargs):
            self.varset_event = event

        def on_registry(event, **kwargs):
            self.registry_event = event

        self.client.add_event_listener(on_VarSet=on_varset, on_Registry=on_registry)
        self.client.fire_recv_event(self.build_event('VarSet'))
        self.assertIsNotNone(self.varset_event)
        self.assertIsNone(self.registry_event)
        self.client.fire_recv_event(self.build_event('Registry'))
        self.assertIsNotNone(self.registry_event)
