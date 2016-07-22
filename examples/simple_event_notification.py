#!/usr/bin/python
import os
import time

from asterisk.ami import AMIClient


def event_notification(source, event):
    os.system('notify-send "%s" "%s"' % (event.name, str(event)))


host = '127.0.0.1'
user = 'admin'
password = 'password'

client = AMIClient(host)
future = client.login(user, password)
if future.response.is_error():
    raise Exception(str(future.response))

client.add_event_listener(event_notification)

try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    client.logoff()
