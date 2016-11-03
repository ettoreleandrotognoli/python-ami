class Action(object):
    def __init__(self, name, keys={}, variables={}):
        self.name = name
        self.keys = keys
        self.variables = variables

    def __str__(self):
        package = 'Action: %s\r\n' % self.name
        for key in self.keys:
            package += '%s: %s\r\n' % (key, self.keys[key])
        for var in self.variables:
            package += 'Variable: %s=%s\r\n' % (var, self.variables[var])
        return package

    def __getattr__(self, item):
        if item in ('name', 'keys', 'variables'):
            return object.__getattr__(self, item)
        return self.keys[item]

    def __setattr__(self, key, value):
        if key in ('name', 'keys', 'variables'):
            return object.__setattr__(self, key, value)
        self.keys[key] = value

    def __setitem__(self, key, value):
        self.variables[key] = value

    def __getitem__(self, item):
        return self.variables[item]


class SimpleAction(Action):
    def __init__(self, name, **kwargs):
        Action.__init__(self, name=name, keys=kwargs)


class LoginAction(Action):
    def __init__(self, username, secret):
        Action.__init__(self, name='Login', keys={'Username': username, 'Secret': secret})


class LogoffAction(Action):
    def __init__(self):
        Action.__init__(self, name='Logoff', keys={})
