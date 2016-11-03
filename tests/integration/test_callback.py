import unittest
from asterisk import ami
from tests.settings import connection, login


class CallbackTest(unittest.TestCase):
    client = None
    response = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)
        self.client.connect()
        self.response = None

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

    def test_originate(self):
        f = self.client.login(**login)
        f.get_response()
        adapter = ami.AMIClientAdapter(self.client)
        self.assertIsNone(self.response)
        f = adapter.Originate(
            Channel='SIP/2010',
            Exten='*65',
            Priority=1,
            Context='from-internal',
            CallerID='python',
            Async=True,
            _callback=self.callback_response
        )
        f.get_response()
        self.assertIsNotNone(self.response)
