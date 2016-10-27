#!/usr/bin/python
import os
import time
from settings import login, connection

from asterisk.ami import AMIClient
from asterisk.ami import EventListener


def event_notification(source, event):
    os.system('notify-send "%s" "%s"' % (event.name, str(event)))


client = AMIClient(**connection)
future = client.login(**login)
if future.response.is_error():
    raise Exception(str(future.response))

client.add_event_listener(EventListener(on_event=event_notification, white_list='Newstate', ChannelStateDesc='Ringing'))

try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    client.logoff()
