import unittest
import re
from random import sample
from asterisk import ami

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
event_name_size = 8
samples_to_test = 10


class WhiteListTest(unittest.TestCase):
    def test_none_white_list(self):
        event_listener = ami.EventListener(white_list=None)
        for i in range(samples_to_test):
            event_name = "".join(sample(letters, event_name_size))
            self.assertTrue(event_listener.check_event_name(event_name))

    def test_empty_white_list(self):
        event_listener = ami.EventListener(white_list=[])
        for i in range(samples_to_test):
            event_name = "".join(sample(letters, event_name_size))
            self.assertFalse(event_listener.check_event_name(event_name))

    def test_string_white_list(self):
        string_rules = list(set(["".join(sample(letters, event_name_size)) for i in range(samples_to_test)]))
        in_white_list = string_rules[:int(len(string_rules) / 2)]
        out_white_list = string_rules[int(len(string_rules) / 2):]
        event_listener = ami.EventListener(white_list=in_white_list)
        for rule in in_white_list:
            self.assertTrue(event_listener.check_event_name(rule))
        for rule in out_white_list:
            self.assertFalse(event_listener.check_event_name(rule))

    def test_regex_white_list(self):
        events = list(set(["".join(sample(letters, event_name_size)) for i in range(samples_to_test)]))
        all_event_listener = ami.EventListener(white_list=re.compile('.*'))
        for event_name in events:
            self.assertTrue(all_event_listener.check_event_name(event_name))
        none_event_listener = ami.EventListener(white_list=[re.compile('[0-9]+')])
        for event_name in events:
            self.assertFalse(none_event_listener.check_event_name(event_name))


class BlackListTest(unittest.TestCase):
    def test_empty_black_list(self):
        event_listener = ami.EventListener(black_list=[])
        for i in range(samples_to_test):
            event_name = sample(letters, event_name_size)
            self.assertTrue(event_listener.check_event_name(event_name))

    def test_string_black_list(self):
        string_rules = list(set(["".join(sample(letters, event_name_size)) for i in range(samples_to_test)]))
        in_black_list = string_rules[:int(len(string_rules) / 2)]
        out_black_list = string_rules[int(len(string_rules) / 2):]
        event_listener = ami.EventListener(black_list=in_black_list)
        for rule in in_black_list:
            self.assertFalse(event_listener.check_event_name(rule))
        for rule in out_black_list:
            self.assertTrue(event_listener.check_event_name(rule))

    def test_regex_black_list(self):
        events = list(set(["".join(sample(letters, event_name_size)) for i in range(samples_to_test)]))
        none_event_listener = ami.EventListener(black_list=re.compile('.*'))
        for event_name in events:
            self.assertFalse(none_event_listener.check_event_name(event_name))
        all_event_listener = ami.EventListener(black_list=[re.compile('[0-9]+')])
        for event_name in events:
            self.assertTrue(all_event_listener.check_event_name(event_name))


class EventListenerTest(unittest.TestCase):
    def build_some_event(self, **kwargs):
        return ami.Event('SomeEvent', kwargs)

    def receive_event(self, event, **kwargs):
        self.assertIsInstance(event, ami.Event)
        return True

    def test_on_event(self):
        event_listener = ami.EventListener(on_event=self.receive_event)
        result = event_listener(event=self.build_some_event(), source=self)
        self.assertTrue(result)

    def test_on_some_event(self):
        event_listener = ami.EventListener(on_SomeEvent=self.receive_event)
        result = event_listener(event=self.build_some_event(), source=self)
        self.assertTrue(result)

    def test_custom_listener(self):
        class SomeEventListener(ami.EventListener):
            def on_SomeEvent(cls, **kwargs):
                return self.receive_event(**kwargs)

        event_listener = SomeEventListener()
        result = event_listener(event=self.build_some_event(), source=self)
        self.assertTrue(result)

    def test_attr_filter(self):
        event_listener = ami.EventListener(on_event=self.receive_event, Value1='teste')
        self.assertIsNone(event_listener(event=self.build_some_event(Value1='null')))
        self.assertTrue(event_listener(event=self.build_some_event(Value1='teste')))
        event_listener = ami.EventListener(on_event=self.receive_event, Value1=re.compile('^t.*'))
        self.assertIsNone(event_listener(event=self.build_some_event(Value1='null')))
        self.assertTrue(event_listener(event=self.build_some_event(Value1='teste')))
