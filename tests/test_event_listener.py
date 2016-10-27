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
        for i in xrange(samples_to_test):
            event_name = "".join(sample(letters, event_name_size))
            self.assertTrue(event_listener.check_event(event_name))

    def test_empty_white_list(self):
        event_listener = ami.EventListener(white_list=[])
        for i in xrange(samples_to_test):
            event_name = "".join(sample(letters, event_name_size))
            self.assertFalse(event_listener.check_event(event_name))

    def test_string_white_list(self):
        string_rules = list(set(["".join(sample(letters, event_name_size)) for i in xrange(samples_to_test)]))
        in_white_list = string_rules[:len(string_rules) / 2]
        out_white_list = string_rules[len(string_rules) / 2:]
        event_listener = ami.EventListener(white_list=in_white_list)
        for rule in in_white_list:
            self.assertTrue(event_listener.check_event(rule))
        for rule in out_white_list:
            self.assertFalse(event_listener.check_event(rule))

    def test_regex_white_list(self):
        events = list(set(["".join(sample(letters, event_name_size)) for i in xrange(samples_to_test)]))
        all_event_listener = ami.EventListener(white_list=[re.compile('.*')])
        for event_name in events:
            self.assertTrue(all_event_listener.check_event(event_name))
        none_event_listener = ami.EventListener(white_list=[re.compile('[0-9]+')])
        for event_name in events:
            self.assertFalse(none_event_listener.check_event(event_name))


class BlackListTest(unittest.TestCase):
    def test_empty_black_list(self):
        event_listener = ami.EventListener(black_list=[])
        for i in xrange(samples_to_test):
            event_name = sample(letters, event_name_size)
            self.assertTrue(event_listener.check_event(event_name))

    def test_string_black_list(self):
        string_rules = list(set(["".join(sample(letters, event_name_size)) for i in xrange(samples_to_test)]))
        in_black_list = string_rules[:len(string_rules) / 2]
        out_black_list = string_rules[len(string_rules) / 2:]
        event_listener = ami.EventListener(black_list=in_black_list)
        for rule in in_black_list:
            self.assertFalse(event_listener.check_event(rule))
        for rule in out_black_list:
            self.assertTrue(event_listener.check_event(rule))

    def test_regex_black_list(self):
        pass
