"""
requirements:
    pip install paho-mqtt
"""
import json
import platform
import time

import paho.mqtt.client as mqtt

from asterisk.ami import EventListener, AMIClient, AutoReconnect
from asterisk.ami.action import SimpleAction
from settings import connection, login

brokers = ['test-mosquitto.org', 'iot.eclipse.org']
broker = brokers[1]
hostname = platform.node()


class MqttAmiBridge(EventListener):
    def __init__(self, base_topic, mqtt_client, ami_client):
        super(MqttAmiBridge, self).__init__()
        self.base_topic = base_topic
        self.mqtt_client = mqtt_client
        self.ami_client = ami_client

    def mqtt_on_connect(self, mqtt_client, userdata, flags, rc):
        mqtt_client.subscribe(self.base_topic + '/+/+')

    def mqtt_on_message(self, mqtt_client, userdata, msg):
        topic_pieces = msg.topic.split('/')
        if topic_pieces[-2] == 'action':
            self.send_action(topic_pieces[-1], msg)

    def send_action(self, action, raw_data):
        try:
            data = json.loads(raw_data.payload) if raw_data.payload != '' else {}
            action = SimpleAction(action, **data)
            self.ami_client.send_action(action, callback=self.send_response)
        except Exception as ex:
            data = {
                'error': str(ex),
                'action': action,
                'data': raw_data.payload
            }
            self.mqtt_client.publish(self.base_topic + '/error', json.dumps(data))

    def send_response(self, response):
        data = {
            'Response': response.status,
            'follows': response.follows,
        }
        data.update(response.keys)
        self.mqtt_client.publish(self.base_topic + '/response', json.dumps(data))

    def on_event(self, event, **kwargs):
        self.mqtt_client.publish(self.base_topic + '/event/%s' % event.name, json.dumps(event.keys))


mqtt_client = mqtt.Client()
ami_client = AMIClient(**connection)
AutoReconnect(ami_client)
bridge = MqttAmiBridge('%s/%s' % (hostname, 'asterisk-ami'), mqtt_client, ami_client)

mqtt_client.on_message = bridge.mqtt_on_message
mqtt_client.on_connect = bridge.mqtt_on_connect
mqtt_client.connect(broker, 1883)
mqtt_client.loop_start()

f = ami_client.login(**login)
ami_client.add_event_listener(bridge)

try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    mqtt_client.disconnect()
    ami_client.logoff()
