#!/usr/bin/env python

import pika

def callback(channel, method, properties, body):
    print channel,method,properties
    print body

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="test_system")
channel.basic_consume(callback, queue="hello_queue", no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
