import unittest
import time

try:
    from thread import start_new_thread
except ImportError:
    from _thread import start_new_thread

from asterisk.ami import Response, FutureResponse


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


TIMEOUT = 0.01


class TestFutureResponse(unittest.TestCase):
    response = None

    def test_callback(self):
        expected = 'some response'

        def callback(response):
            self.response = response

        future = FutureResponse(callback=callback)
        future.response = expected
        self.assertEqual(future.response, expected)
        self.assertEqual(self.response, expected)

    def test_lock_timeout(self):
        future = FutureResponse(timeout=TIMEOUT)
        before = time.time()
        response = future.response
        after = time.time()
        diff = after - before
        self.assertIsNone(response)
        self.assertAlmostEqual(diff, TIMEOUT, delta=0.1)

    def test_lock(self):
        expected = 'some respone'
        future = FutureResponse()

        def runnable():
            time.sleep(TIMEOUT)
            future.response = expected

        start_new_thread(runnable, (), {})
        response = future.response
        self.assertEqual(response, expected)
