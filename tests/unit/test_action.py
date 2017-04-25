import unittest

from asterisk.ami import LoginAction, LogoffAction, SimpleAction


class AMIActionTest(unittest.TestCase):
    def compare_actions(self, a1, a2):
        a1 = str(a1).split('\r\n')
        a2 = str(a2).split('\r\n')
        self.assertEqual(a1[0], a2[0])
        self.assertSetEqual(set(a1[1:]), set(a2[1:]))

    def test_login_action(self):
        expected = '\r\n'.join([
            'Action: Login',
            'Username: username',
            'Secret: password',
        ]) + '\r\n'
        action = LoginAction('username', 'password')
        self.compare_actions(action, expected)
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
        self.compare_actions(action, expected)
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
        self.compare_actions(action, expected)
        self.assertEqual(action.Channel, 'channel-1')
        self.assertEqual(action['<Variable 1>'], '<Value 1>')
        action.Channel = 'channel-2'
        self.assertEqual(action.Channel, 'channel-2')
