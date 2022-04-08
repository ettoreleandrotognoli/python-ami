import socket
import threading

from rx import Observable


class AMIMock(object):
    thread = None

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.socket.bind((socket.gethostname(), 0,))
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        return self.socket.getsockname()

    def run(self):
        self.socket.listen(5)

        def clients_iter():
            try:
                while True:
                    yield self.socket.accept()
            except:
                pass

        def send_start(c):
            return c[0].send(b'Asterisk Call Manager/6.6.6\r\n\r\n')

        Observable.from_(clients_iter()) \
            .subscribe(send_start)

    def stop(self):
        self.socket.close()
        self.thread.join(1)
