import time
import unittest

from asterisk.ami import AMIClient
from mock_ami import AMIMock
from tests.settings import login


class ConnectionTest(unittest.TestCase):
    def setUp(self):
        self.server = AMIMock()
        self.server_address = self.server.start()
        time.sleep(0.2)

    def tearDown(self):
        self.server.stop()

    def test_start(self):
        client = AMIClient(**dict(zip(('address', 'port'), self.server_address)))
        client.connect()
        time.sleep(0.5)
        self.assertEqual(client._ami_version, '6.6.6')
        client.login(**login)
        client.disconnect()
