import unittest
from asterisk import ami
from tests.settings import connection, login


class CommandTest(unittest.TestCase):
    client = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)
        f = self.client.login(**login)
        f.get_response()

    def tearDown(self):
        future = self.client.logoff()
        if future is not None:
            future.get_response()
        self.client.disconnect()

    def test_command_show_channels(self):
        adapter = ami.AMIClientAdapter(self.client)
        f = adapter.Command(command='core show channels')
        self.assertIsNotNone(f.response.follows)
