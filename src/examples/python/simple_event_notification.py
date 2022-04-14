#!/usr/bin/python
import os
import time
from settings import login, connection

from asterisk.ami import AMIClient


def event_notification(source, event):
    os.system('notify-send "%s" "%s"' % (event.name, str(event)))


client = AMIClient(**connection)
future = client.login(**login)
if future.response.is_error():
    raise Exception(str(future.response))

client.add_event_listener(event_notification)

try:
    client.wait()
except (KeyboardInterrupt, SystemExit):
    client.logoff()
