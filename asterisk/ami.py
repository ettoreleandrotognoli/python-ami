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
        for i in range(1, len(lines)):
            (key, value) = lines[i].split(": ", 1)
            keys[key] = value
        return Response(status, keys)

    @staticmethod
    def match(response):
        return bool(Response.match_regex.match(str(response)))

    def __init__(self, status, keys):
        self.status = status
        self.keys = keys

    def __str__(self):
        package = "Response: %s\r\n" % self.status
        for key in self.keys:
            package += "%s: %s\r\n" % (key, self.keys[key])
        return package


class FutureResponse(object):
    def __init__(self, timeout=None):
        self.timeout = timeout
        self._response = None
        self._lock = threading.Condition()

    def set_response(self, response):
        self._lock.acquire()
        self._response = response
        self._lock.notifyAll()
        self._lock.release()

    def get_response(self):
        if self._response is not None:
            return self._response
        self._lock.acquire()
        self._lock.wait(self.timeout)
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
            (key, value) = lines[i].split(': ', 1)
            keys[key] = value
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

    _futures = {}
    _event_listeners = []

    def __init__(self, address, port, buffer_size=1025):
        self.listeners = []
        self.address = address
        self.buffer_size = buffer_size
        self.port = port
        self.socket = None
        self._thread = None
        self._on = False
        self.ami_version = None

    def next_action_id(self):
        id = self.action_counter
        self.action_counter += 1
        return str(id)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))
        self._on = True
        self._thread = threading.Thread(target=self.listen)
        self._thread.start()

    def login(self, username, secret):
        if not self._on:
            self.connect()
        return self.send_action(LoginAction(username, secret))

    def logoff(self):
        if not self._on:
            return
        return self.send_action(LogoffAction())

    def send_action(self, action):
        if 'ActionID' not in action.keys:
            action_id = self.next_action_id()
            action.keys['ActionID'] = action_id
        else:
            action_id = action.keys['ActionID']
        future = FutureResponse()
        self._futures[action_id] = future
        self.send(action)
        return future

    def send(self, pack):
        self.socket.send(str(pack) + "\r\n")

    def listen(self):
        asterisk_start = self.socket.recv(self.buffer_size)
        match = AMIClient.asterisk_start_regex.match(asterisk_start)
        if not match:
            raise Exception()
        self.ami_version = match.group('version')
        pack = ""
        while self._on:
            data = self.socket.recv(self.buffer_size)
            if not data:
                continue
            pack += data
            if not (pack.endswith("\r\n\r\n") or pack.endswith("\n\n")):
                continue
            self.fire_recv_pack(pack)
            pack = ""
        self.socket.close()

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
        if pack.endswith('\r\n\r\n'):
            pack = pack[0: - 4]
        if pack.endswith('\n\n'):
            pack = pack[0:- 2]
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

    def _action(self, name, variables={}, **kwargs):
        action = Action(name, kwargs)
        action.variables = variables
        return self._ami_client.send_action(action)

    def __getattr__(self, item):
        return partial(self._action, item)
