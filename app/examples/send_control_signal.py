#!/usr/bin/env python
import pika
from flask import json
import time
import sys

queue_name = "8a6084dc970f4cbfb49e44eb02c7659f"

# establish connection with rabbitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue=queue_name, durable=True) # create a queue
control_signal = {"u": int(sys.argv[1])}
channel.basic_publish("", routing_key=queue_name,
    body=json.dumps({"control": control_signal}),
    properties=pika.BasicProperties(content_type="application/json"))

print("control signal sent!")
connection.close()
