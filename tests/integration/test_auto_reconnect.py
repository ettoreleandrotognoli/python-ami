import unittest
from asterisk import ami
from tests.settings import connection, login


def debug(*args, **kwargs):
    print(map(str, args), map(lambda t: map(str, t), kwargs.items()))


class AutoReconnectTest(unittest.TestCase):
    client = None
    auto_reconnect = None
    response = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)
        self.auto_reconnect = ami.AutoReconnect(
            self.client,
            on_reconnect=debug,
            on_disconnect=debug,
        )

    def tearDown(self):
        future = self.client.logoff()
        if future is not None:
            future.get_response()
        self.client.disconnect()

    def callback_response(self, response):
        self.response = response

    def test_login(self):
        self.assertIsNone(self.response)
        f = self.client.login(callback=self.callback_response, **login)
        f.get_response()
        self.assertIsNotNone(self.response)
        #import time
        #time.sleep(30)
