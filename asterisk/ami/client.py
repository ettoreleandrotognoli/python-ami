import re
import socket
from functools import partial
import threading

from .action import *
from .response import *
from .event import *


class AMIClient(object):
    asterisk_start_regex = re.compile('^Asterisk *Call *Manager/(?P<version>([0-9]+\.)*[0-9]+)', re.IGNORECASE)
    asterisk_line_regex = re.compile('\r?\n', re.IGNORECASE | re.MULTILINE)
    asterisk_pack_regex = re.compile('\r?\n\r?\n', re.IGNORECASE | re.MULTILINE)

    def __init__(self, address, port=5038, timeout=1000, buffer_size=2 ** 10):
        self._action_counter = 0
        self._futures = {}
        self._event_listeners = []
        self._address = address
        self._buffer_size = buffer_size
        self._port = port
        self._socket = None
        self._thread = None
        self._on = False
        self._ami_version = None
        self._timeout = timeout

    def next_action_id(self):
        id = self._action_counter
        self._action_counter += 1
        return str(id)

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._address, self._port))
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
        future = FutureResponse(callback, self._timeout)
        self._futures[action_id] = future
        self.send(action)
        return future

    def send(self, pack):
        self._socket.send(bytearray(str(pack) + "\r\n", 'utf-8'))

    def _next_pack(self):
        data = ''
        while self._on:
            recv = self._socket.recv(self._buffer_size).decode('utf-8')
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
            recv = self._socket.recv(self._buffer_size).decode('utf-8')
            if recv == '':
                self._on = False
                continue
            data += recv
        self._socket.close()

    def listen(self):
        pack_generator = self._next_pack()
        asterisk_start = next(pack_generator)
        match = AMIClient.asterisk_start_regex.match(asterisk_start)
        if not match:
            raise Exception()
        self._ami_version = match.group('version')
        try:
            while self._on:
                pack = next(pack_generator)
                self.fire_recv_pack(pack)
        except Exception as ex:
            print(ex)

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

    def add_event_listener(self, on_event=None, **kwargs):
        if len(kwargs) > 0 and not isinstance(on_event, EventListener):
            event_listener = EventListener(on_event=on_event, **kwargs)
        else:
            event_listener = on_event
        self._event_listeners.append(event_listener)
        return event_listener

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
