import logging
from flask import json
import pika


LOGGER = logging.getLogger(__name__)

class MQServer:
    '''RabbitMQ server using advanced message queuing protocol (AMQP)'''

    def __init__(self, queue_name, host_name="localhost"):

        # Setup AMQP
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_name))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.consumer_callback, queue=queue_name, no_ack=False)
        #self.channel.start_consuming()


    def consumer_callback(self, channel, method, properties, body):
        """
        Callback method automatically invoked when the blocking method
        channel.start_consuming() is used
        """

        LOGGER.info("Message received")

        # # Acknowledge the message
        self.channel.basic_ack(method.delivery_tag)

        payload = json.loads(body)
        print(payload)

        # see if the message contains a control signal
        if isinstance(payload, dict) and "control" in payload:
            LOGGER.info("A control signal received!")
            #self.set_control(payload["control"])


    def __del__(self):
        # if self.consumer_tag:
        #     self.channel.basic_cancel(self.consumer_tag)
        self.connection.close()
