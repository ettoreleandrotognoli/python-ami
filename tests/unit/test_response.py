import unittest
from asterisk.ami import Response


class AMIResponseTest(unittest.TestCase):
    def test_login_response(self):
        login_response = '\r\n'.join([
            'Response: Success',
            'Message: Authentication accepted',
        ]) + '\r\n'
        self.assertTrue(Response.match(login_response))
        response = Response.read(login_response)
        self.assertFalse(response.is_error())
        self.assertIsNone(response.follows)
        self.assertEqual(login_response, str(response))

    def test_login_response_fail(self):
        login_response = '\r\n'.join([
            'Response: Error',
            'Message: Authentication failed',
        ]) + '\r\n'
        self.assertTrue(Response.match(login_response))
        response = Response.read(login_response)
        self.assertTrue(response.is_error())
        self.assertIsNone(response.follows)
        self.assertEqual(login_response, str(response))

    def test_goodbye_response(self):
        goodbye_response = '\r\n'.join([
            'Response: Goodbye',
            'Message: Thanks for all the fish.'
        ]) + '\r\n'
        self.assertTrue(Response.match(goodbye_response))
        response = Response.read(goodbye_response)
        self.assertFalse(response.is_error())
        self.assertIsNone(response.follows)
        self.assertEqual(goodbye_response, str(response))

    def test_with_follows(self):
        follows_response = '\r\n'.join([
            'Response: Follows',
            'Channel (Context Extension Pri ) State Appl. Data',
            '0 active channel(s)',
            '--END COMMAND--',
        ]) + '\r\n'
        self.assertTrue(Response.match(follows_response))
        response = Response.read(follows_response)
        self.assertFalse(response.is_error())
        self.assertIsNotNone(response.follows)
        self.assertListEqual(follows_response.split('\r\n')[1:-1], response.follows)
        self.assertEqual(follows_response, str(response))

    def test_event(self):
        event = '\r\n'.join([
            'Event: FullyBooted',
            'Privilege: system, all',
            'Status: Fully Booted',
        ])
        self.assertFalse(Response.match(event))
        with self.assertRaises(Exception):
            Response.read(event)
