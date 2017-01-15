import re
import threading


class Response(object):
    match_regex = re.compile('^Response: .*', re.IGNORECASE)

    @staticmethod
    def read(response):
        lines = response.splitlines()
        (key, value) = lines[0].split(': ', 1)
        if not key.lower() == 'response':
            raise Exception()
        status = value
        keys = {}
        follows = [] if status.lower() == 'follows' else None
        for line in lines[1:]:
            try:
                (key, value) = line.split(': ', 1)
                keys[key] = value
            except:
                if follows is not None:
                    follows.append(line)
        return Response(status, keys, follows)

    @staticmethod
    def match(response):
        return bool(Response.match_regex.match(response))

    def __init__(self, status, keys={}, fallows=None):
        self.status = status
        self.keys = keys
        self.follows = fallows

    def __str__(self):
        package = 'Response: %s\r\n' % self.status
        for key in self.keys:
            package += '%s: %s\r\n' % (key, self.keys[key])
        if self.follows is not None and len(self.follows) > 0:
            package += '\r\n'.join(self.follows) + '\r\n'
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
            print(ex)
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
