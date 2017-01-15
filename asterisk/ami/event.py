import re

try:
    unicode = unicode
except NameError:
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class Event(object):
    match_regex = re.compile('^Event: .*', re.IGNORECASE)
    parsers = {}

    @staticmethod
    def register_parser(*event_name):
        def wrapper(parser):
            for name in event_name:
                Event.parsers[name] = parser

        return wrapper

    @staticmethod
    def read(event):
        lines = event.splitlines()
        (key, value) = lines[0].split(': ', 1)
        if not key.lower() == 'event':
            raise Exception()
        name = value
        keys = {}
        for i in range(1, len(lines)):
            try:
                (key, value) = lines[i].split(': ', 1)
                if key in Event.parsers:
                    Event.parsers[key](name, keys)(key, value)
                else:
                    keys[key] = value
            except:
                pass
        return Event(name, keys)

    @staticmethod
    def match(event):
        return bool(Event.match_regex.match(event))

    def __init__(self, name, keys={}):
        self.name = name
        self.keys = keys

    def __getitem__(self, item):
        return self.keys[item]

    def __setitem__(self, key, value):
        self.keys[key] = value

    def __iter__(self):
        return iter(self.keys)

    def __str__(self):
        return 'Event : %s -> %s' % (self.name, self.keys)


class EventKeyParser(object):
    def __init__(self, event, keys):
        self.event = event
        self.keys = keys

    def __call__(self, key, value):
        raise NotImplementedError()


@Event.register_parser('ChanVariable', 'DestChanVariable')
class KeyValueParser(EventKeyParser):
    def __call__(self, key, value):
        if key not in self.keys:
            self.keys[key] = {}
        k, v = value.split('=', 1)
        self.keys[key][k] = v


class EventListener(object):
    def __init__(self, on_event=None, white_list=None, black_list=[], **kwargs):
        self.white_list = [white_list] if isinstance(white_list, (basestring, re._pattern_type)) else white_list
        self.black_list = [black_list] if isinstance(black_list, (basestring, re._pattern_type)) else black_list
        for k in list(kwargs.keys()):
            if k.startswith('on_'):
                setattr(self, k, kwargs.pop(k))
        self.assert_attrs = kwargs
        if on_event is None:
            self.on_event = getattr(self, 'on_event', self._on_event)
        else:
            self.on_event = on_event

    def check_white_list(self, event_name):
        if self.white_list is None:
            return True
        for rule in self.white_list:
            if isinstance(rule, basestring) and event_name == rule:
                return True
            if isinstance(rule, re._pattern_type) and rule.search(event_name) is not None:
                return True
        return False

    def check_black_list(self, event_name):
        for rule in self.black_list:
            if isinstance(rule, basestring) and event_name == rule:
                return False
            if isinstance(rule, re._pattern_type) and rule.match(event_name) is not None:
                return False
        return True

    def check_attribute(self, rules, value):
        if isinstance(rules, (re._pattern_type, basestring)):
            rules = [rules]
        for rule in rules:
            if isinstance(rule, basestring) and rule == value:
                return True
            if isinstance(rule, re._pattern_type) and rule.search(value):
                return True
        return False

    def check_attributes(self, event_keys):
        for k, rule in self.assert_attrs.items():
            if k not in event_keys:
                continue
            value = event_keys[k]
            if self.check_attribute(rule, value) is False:
                return False
        return True

    def check_event_name(self, event_name):
        return self.check_white_list(event_name) and self.check_black_list(event_name)

    def check_event(self, event):
        if self.check_event_name(event.name) and self.check_attributes(event.keys):
            return True
        return False

    def __call__(self, event, **kwargs):
        if self.check_event(event):
            return self.on_event(event=event, **kwargs)
        return None

    def _on_event(self, **kwargs):
        event_name = kwargs['event'].name
        method_name = 'on_%s' % event_name
        return getattr(self, method_name, lambda *args, **ks: None)(**kwargs)
