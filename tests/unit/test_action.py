import unittest

from asterisk.ami import LoginAction, LogoffAction
from asterisk.ami.action import SimpleAction


class AMIActionTest(unittest.TestCase):
    def test_login_action(self):
        expected = '\r\n'.join([
            'Action: Login',
            'Username: username',
            'Secret: password',
        ]) + '\r\n'
        action = LoginAction('username', 'password')
        self.assertEqual(expected, str(action))
        self.assertEqual(action.name, 'Login')
        self.assertEqual(action.Username, 'username')
        self.assertEqual(action.Secret, 'password')
        self.assertDictEqual(action.keys, {'Username': 'username', 'Secret': 'password'})
        self.assertEqual(len(action.variables), 0)

    def test_logoff_action(self):
        expected = '\r\n'.join([
            'Action: Logoff',
        ]) + '\r\n'
        action = LogoffAction()
        self.assertEqual(expected, str(action))
        self.assertEqual(action.name, 'Logoff')
        self.assertEqual(len(action.keys), 0)
        self.assertEqual(len(action.variables), 0)

    def test_with_variable(self):
        expected = '\r\n'.join([
            'Action: GetVar',
            'Channel: channel-1',
            'Variable: <Variable 1>=<Value 1>',
        ]) + '\r\n'
        action = SimpleAction('GetVar', Channel='channel-1')
        action['<Variable 1>'] = '<Value 1>'
        self.assertEqual(expected, str(action))
        self.assertEqual(action.Channel, 'channel-1')
        self.assertEqual(action['<Variable 1>'], '<Value 1>')
        action.Channel = 'channel-2'
        self.assertEqual(action.Channel, 'channel-2')
