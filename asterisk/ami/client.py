import re
import socket
import threading
from functools import partial

from .action import Action, LoginAction, LogoffAction
from .event import Event, EventListener
from .response import Response, FutureResponse

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


class AMIClient(object):
    asterisk_start_regex = re.compile('^Asterisk *Call *Manager/(?P<version>([0-9]+\.)*[0-9]+)', re.IGNORECASE)
    asterisk_line_regex = re.compile(b'\r?\n', re.IGNORECASE | re.MULTILINE)
    asterisk_pack_regex = re.compile(b'\r?\n\r?\n', re.IGNORECASE | re.MULTILINE)

    def __init__(self, address, port=5038, timeout=3, buffer_size=2 ** 10):
        self._action_counter = 0
        self._futures = {}
        self._event_listeners = []
        self._address = address
        self._buffer_size = buffer_size
        self._port = port
        self._socket = None
        self._thread = None
        self.finished = None
        self._ami_version = None
        self._timeout = timeout

    def next_action_id(self):
        id = self._action_counter
        self._action_counter += 1
        return str(id)

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._address, self._port))
        self.finished = threading.Event()
        self._thread = threading.Thread(target=self.listen)
        self._thread.daemon = True
        self._thread.start()

    def disconnect(self):
        self.finished.set()
        try:
            self._thread.join()
        except:
            pass

    def login(self, username, secret, callback=None):
        if self.finished is None or self.finished.is_set():
            self.connect()
        return self.send_action(LoginAction(username, secret), callback)

    def logoff(self, callback=None):
        if self.finished is None or self.finished.is_set():
            return
        return self.send_action(LogoffAction(), callback)

    def send_action(self, action, callback=None):
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
        self._socket.send(bytearray(unicode(pack) + '\r\n', 'utf-8'))

    def _next_pack(self):
        data = b''
        while not self.finished.is_set():
            recv = self._socket.recv(self._buffer_size)
            if recv == b'':
                self.finished.set()
                continue
            data += recv
            if self.asterisk_line_regex.search(data):
                (pack, data) = self.asterisk_line_regex.split(data, 1)
                yield pack.decode('utf-8')
                break
        while not self.finished.is_set():
            while self.asterisk_pack_regex.search(data):
                (pack, data) = self.asterisk_pack_regex.split(data, 1)
                yield pack.decode('utf-8')
            recv = self._socket.recv(self._buffer_size)
            if recv == b'':
                self.finished.set()
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
            while not self.finished.is_set():
                pack = next(pack_generator)
                self.fire_recv_pack(pack)
        except Exception as ex:
            print(ex)

    def fire_recv_reponse(self, response):
        if response.status.lower() == 'goodbye':
            self.finished.set()
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


class AutoReconnect(threading.Thread):
    def __init__(self, ami_client, delay=0.5,
                 on_disconnect=lambda *args: None, on_reconnect=lambda *args: None):
        super(AutoReconnect, self).__init__()
        self.on_reconnect = on_reconnect
        self.on_disconnect = on_disconnect
        self.delay = delay
        self.finished = None
        self._ami_client = ami_client
        self._login_args = None
        self._login = None
        self._logoff = None
        self._prepare_client()

    def _prepare_client(self):
        self._login = self._ami_client.login
        self._logoff = self._ami_client.logoff
        self._ami_client.login = self._login_wrapper
        self._ami_client.logoff = self._logoff_wrapper

    def _rollback_client(self):
        self._ami_client.login = self._login
        self._ami_client.logoff = self._logoff

    def _login_wrapper(self, *args, **kwargs):
        callback = kwargs.pop('callback', None) or (lambda *a, **k: None)

        def on_login(response, *a, **k):
            if not response.is_error():
                if self._login_args is None:
                    self.finished = threading.Event()
                    self.start()
                self._login_args = (args, kwargs)
            callback(response, *a, **k)

        kwargs['callback'] = on_login
        return self._login(*args, **kwargs)

    def _logoff_wrapper(self, *args, **kwargs):
        self.finished.set()
        self._rollback_client()
        return self._logoff(*args, **kwargs)

    def ping(self):
        try:
            f = self._ami_client.send_action(Action('Ping'))
            response = f.response
            if response is not None and not response.is_error():
                return True
            self.on_disconnect(self._ami_client, response)
        except Exception as ex:
            self.on_disconnect(self._ami_client, ex)
        return False

    def try_reconnect(self):
        try:
            f = self._login(*self._login_args[0], **self._login_args[1])
            response = f.response
            if response is not None and not response.is_error():
                self.on_reconnect(self._ami_client, response)
                return True
        except:
            pass
        return False

    def run(self):
        self.finished.wait(self.delay)
        while not self.finished.is_set():
            if not self.ping():
                self.try_reconnect()
            self.finished.wait(self.delay)

    def __del__(self):
        self._rollback_client()
