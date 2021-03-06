#!/usr/bin/python

import sys
import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Parameters
host = "a2ixc5bjabbknt.iot.us-east-1.amazonaws.com"
rootCAPath =  "/home/pi/SensorData/cert/root-CA.crt"
certificatePath = "/home/pi/SensorData/cert/iotsrv03.cert.pem"
privateKeyPath = "/home/pi/SensorData/cert/iotsrv03.private.key"
useWebsocket = False
clientId = "iotsrv03"
topic = "SensorData/Measurements"
location = "home"

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, 443)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Built message
message = {}
message['device'] = clientId
message['loc'] = location
message['timestamp'] = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
message['temperature'] = '{0:0.1f}'.format(30)
message['humidity'] = '{0:0.1f}'.format(85)
messageJson = json.dumps(message)

# Publish to the same topic in a loop forever
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.publish(topic, messageJson, 1)
print('Published topic %s: %s\n' % (topic, messageJson))
