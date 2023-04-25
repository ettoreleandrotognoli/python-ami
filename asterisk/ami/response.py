import re
import threading


class Response(object):
    match_regex = re.compile('^Response: .*', re.IGNORECASE)
    key_regex = re.compile(r'^[a-zA-Z0-9_\-]+$')

    @staticmethod
    def read(response):
        lines = response.splitlines()
        (key, value) = map(lambda s: s.strip(), lines[0].split(':', 1))
        if not key.lower() == 'response':
            raise Exception()
        status = value
        keys = {}
        follows = []
        keys_and_follows = iter(lines[1:])
        for line in keys_and_follows:
            if not line:
                continue
            try:
                (key, value) = line.split(':', 1)
                if not Response.key_regex.match(key):
                    raise key
                k = key.strip()
                if k in keys:
                    keys[k] += f"\n{value.strip()}"
                else:
                    keys[k] = value.strip()
            except:
                follows.append(line)
                break
        for line in keys_and_follows:
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
        if self.follows:
            package += '\n'.join(self.follows) + '\r\n'
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
            traceback.print_exc()
        finally:
            self._lock.acquire()
            self._response = response
            self._lock.notifyAll()
            self._lock.release()

    def get_response(self):
        self._lock.acquire()
        if self._response is not None:
            self._lock.release()
            return self._response
        self._lock.wait(self._timeout)
        self._lock.release()
        return self._response

    response = property(get_response, set_response)
