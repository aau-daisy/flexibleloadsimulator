#!/usr/bin/env python
import pika
from flask import json
import time

# establish connection with rabbitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="test_system") # create a queue
channel.basic_publish("", routing_key="test_system",
    body=json.dumps({"control": "{\"u\":1}"}),
    properties=pika.BasicProperties(content_type="application/json"))


print("control signal sent!")
connection.close()
