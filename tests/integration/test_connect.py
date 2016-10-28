import unittest
from asterisk import ami
from tests.settings import connection, login


class LoginTest(unittest.TestCase):
    client = None

    def setUp(self):
        self.client = ami.AMIClient(**connection)
        self.client.connect()

    def tearDown(self):
        future = self.client.logoff()
        if future is not None:
            future.get_response()
        self.client.disconnect()

    def test_success_login(self):
        future = self.client.login(**login)
        self.assertIsNotNone(future.response)

    def test_error_login(self):
        future = self.client.login('user', 'pass321')
        self.assertTrue(future.response.is_error())
