__author__ = 'ettore'
import re
import socket
import threading
from functools import partial


class Action(object):
    def __init__(self, name, keys={}, variables={}):
        self.name = name
        self.keys = keys
        self.variables = variables

    def __str__(self):
        package = "Action: %s\r\n" % self.name
        for key in self.keys:
            package += "%s: %s\r\n" % (key, self.keys[key])
        for var in self.variables:
            package += "Variable: %s=%s\r\n" % (var, self.variables[var])
        return package

    def __getattr__(self, item):
        if item in ('name', 'keys', 'variables'):
            return object.__getattr__(self, item)
        return self.keys[item]

    def __setattr__(self, key, value):
        if key in ('name', 'keys', 'variables'):
            return object.__setattr__(self, key, value)
        self.keys[key] = value

    def __setitem__(self, key, value):
        self.variables[key] = value

    def __getitem__(self, item):
        return self.variables[item]


class Response(object):
    match_regex = re.compile('^Response: .*', re.IGNORECASE)

    @staticmethod
    def read(response):
        lines = str(response).splitlines()
        (key, value) = lines[0].split(": ", 1)
        if not key.lower() == 'response':
            raise Exception()
        status = value
        keys = {}
        follows = [] if status.lower() == 'follows' else None
        for line in lines[1:]:
            try:
                (key, value) = line.split(": ", 1)
                keys[key] = value
            except:
                if follows is not None:
                    follows.append(line)
        return Response(status, keys, follows)

    @staticmethod
    def match(response):
        return bool(Response.match_regex.match(str(response)))

    def __init__(self, status, keys={}, fallows=None):
        self.status = status
        self.keys = keys
        self.follows = fallows

    def __str__(self):
        package = "Response: %s\r\n" % self.status
        for key in self.keys:
            package += "%s: %s\r\n" % (key, self.keys[key])
        if self.follows is not None and len(self.follows) > 0:
            package += "\r\n".join(self.follows) + "\r\n"
        return package

    def is_error(self):
        return self.status.lower() == 'error'


class FutureResponse(object):
    def __init__(self, callback=None, timeout=None):
        self._timeout = timeout
        self._response = None
        self._lock = threading.Condition()
        self._callback = callback

    def set_response(self, response):
        try:
            if self._callback is not None:
                self._callback(response)
        except Exception as ex:
            print ex
        self._lock.acquire()
        self._response = response
        self._lock.notifyAll()
        self._lock.release()

    def get_response(self):
        if self._response is not None:
            return self._response
        self._lock.acquire()
        self._lock.wait(self._timeout)
        self._lock.release()
        return self._response

    response = property(get_response, set_response)


class Event(object):
    match_regex = re.compile('^Event: .*', re.IGNORECASE)

    @staticmethod
    def read(event):
        lines = str(event).splitlines()
        (key, value) = lines[0].split(': ', 1)
        if not key.lower() == 'event':
            raise Exception()
        name = value
        keys = {}
        for i in range(1, len(lines)):
            try:
                (key, value) = lines[i].split(': ', 1)
                keys[key] = value
            except:
                pass
        return Event(name, keys)

    @staticmethod
    def match(event):
        return bool(Event.match_regex.match(str(event)))

    def __init__(self, name, keys):
        self.name = name
        self.keys = keys

    def __str__(self):
        return 'Event : %s -> %s' % (self.name, self.keys)


class SimpleAction(Action):
    def __init__(self, name, **kwargs):
        Action.__init__(self, name=name, keys=kwargs)


class LoginAction(Action):
    def __init__(self, username, secret):
        Action.__init__(self, name='Login', keys={'Username': username, 'Secret': secret})


class LogoffAction(Action):
    def __init__(self):
        Action.__init__(self, name='Logoff', keys={})


class AMIClient(object):
    action_counter = 0
    asterisk_start_regex = re.compile('^Asterisk *Call *Manager/(?P<version>([0-9]+\.)*[0-9]+)', re.IGNORECASE)
    asterisk_line_regex = re.compile('\r?\n', re.IGNORECASE | re.MULTILINE)
    asterisk_pack_regex = re.compile('\r?\n\r?\n', re.IGNORECASE | re.MULTILINE)

    _futures = {}
    _event_listeners = []

    def __init__(self, address, port=5038, timeout=1000, buffer_size=2 ** 10):
        self.listeners = []
        self.address = address
        self.buffer_size = buffer_size
        self.port = port
        self._socket = None
        self._thread = None
        self._on = False
        self.ami_version = None
        self.timeout = timeout

    def next_action_id(self):
        id = self.action_counter
        self.action_counter += 1
        return str(id)

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.address, self.port))
        self._on = True
        self._thread = threading.Thread(target=self.listen)
        self._thread.start()

    def disconnect(self):
        self._on = False
        try:
            self._thread.join()
        except:
            pass

    def login(self, username, secret, callback=None):
        if not self._on:
            self.connect()
        return self.send_action(LoginAction(username, secret), callback)

    def logoff(self, callback=None):
        if not self._on:
            return
        return self.send_action(LogoffAction(), callback)

    def send_action(self, action, callback):
        if 'ActionID' not in action.keys:
            action_id = self.next_action_id()
            action.keys['ActionID'] = action_id
        else:
            action_id = action.keys['ActionID']
        future = FutureResponse(callback, self.timeout)
        self._futures[action_id] = future
        self.send(action)
        return future

    def send(self, pack):
        self._socket.send(str(pack) + "\r\n")

    def _next_pack(self):
        data = ''
        while self._on:
            recv = self._socket.recv(self.buffer_size)
            if recv == '':
                self._on = False
                continue
            data += recv
            if self.asterisk_line_regex.search(data):
                (pack, data) = self.asterisk_line_regex.split(data, 1)
                yield pack
                break
        while self._on:
            while self.asterisk_pack_regex.search(data):
                (pack, data) = self.asterisk_pack_regex.split(data, 1)
                yield pack
            recv = self._socket.recv(self.buffer_size)
            if recv == '':
                self._on = False
                continue
            data += recv
        self._socket.close()

    def listen(self):
        pack_generator = self._next_pack()
        asterisk_start = pack_generator.next()
        match = AMIClient.asterisk_start_regex.match(asterisk_start)
        if not match:
            raise Exception()
        self.ami_version = match.group('version')
        try:
            while self._on:
                pack = pack_generator.next()
                self.fire_recv_pack(pack)
        except Exception as ex:
            print ex

    def fire_recv_reponse(self, response):
        if response.status.lower() == 'goodbye':
            self._on = False
        if 'ActionID' not in response.keys:
            return
        action_id = response.keys['ActionID']
        if action_id not in self._futures:
            return
        future = self._futures.pop(action_id)
        future.response = response

    def fire_recv_event(self, event):
        for listener in self._event_listeners:
            listener(event=event, source=self)

    def fire_recv_pack(self, pack):
        if Response.match(pack):
            response = Response.read(pack)
            self.fire_recv_reponse(response)
        if Event.match(pack):
            event = Event.read(pack)
            self.fire_recv_event(event)

    def add_event_listener(self, event_listener):
        self._event_listeners.append(event_listener)

    def remove_event_listener(self, event_listener):
        self._event_listeners.remove(event_listener)


class AMIClientAdapter(object):
    def __init__(self, ami_client):
        self._ami_client = ami_client

    def _action(self, name, _callback=None, variables={}, **kwargs):
        action = Action(name, kwargs)
        action.variables = variables
        return self._ami_client.send_action(action, _callback)

    def __getattr__(self, item):
        return partial(self._action, item)


class EventListener(object):
    def __init__(self, white_list=None, black_list=[], on_event=None, **kwargs):
        self.white_list = [white_list] if isinstance(white_list, (basestring, re._pattern_type)) else white_list
        self.black_list = [black_list] if isinstance(black_list, (basestring, re._pattern_type)) else black_list
        for k in kwargs.keys():
            if k.startswith('on_'):
                setattr(self, k, kwargs.pop(k))
        self.assert_attrs = kwargs
        if on_event is None:
            self.on_event = self._on_event
        else:
            self.on_event = on_event

    def check_white_list(self, event_name):
        if self.white_list is None:
            return True
        for rule in self.white_list:
            if isinstance(rule, basestring) and event_name == rule:
                return True
            if isinstance(rule, re._pattern_type) and rule.match(event_name) is not None:
                return True
        return False

    def check_black_list(self, event_name):
        for rule in self.black_list:
            if isinstance(rule, basestring) and event_name == rule:
                return False
            if isinstance(rule, re._pattern_type) and rule.match(event_name) is not None:
                return False
        return True

    def check_attributes(self, event_keys):
        for k, v in self.assert_attrs.items():
            if k not in event_keys:
                continue
            value = event_keys[k]
            if isinstance(v, basestring) and v != value:
                return False
            if isinstance(v, re._pattern_type) and v.match(value) is None:
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
