import pika
import json
import logging

LOGGER = logging.getLogger(__name__)


class AMQPService:
    hostname = None
    queue_name = None
    connection = None
    channel = None

    def __init__(self, queue_name):
        self.hostname = 'localhost'
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.hostname))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)

        # not working with our code because it operates in blocking mode
        # self.channel.basic_consume(self.on_message, self.queue_name, no_ack=False)
        # self.channel.start_consuming()

    def consume_messages(self):
        """
        We manually fetch messages from AMQP queue because the callback
        method in channel.basic_consum() is blocking type
        """

        method_frame, properties, body = self.channel.basic_get(self.queue_name, no_ack=False)

        while method_frame:

            LOGGER.info("Message received")

            self.channel.basic_ack(method_frame.delivery_tag)
            payload = json.loads(body)
            if not isinstance(payload, dict):
                return

            # Process the message
            if 'control' in payload:
                LOGGER.info("A control signal received!")
                # self.set_control(payload['control'])
                print(payload['control'])

            # Continue getting messages
            method_frame, properties, body = self.channel.basic_get(self.queue_name, no_ack=False)

        # TODO
        # return control_signal

    def produce_messages(self, device_id, measurements):
        """
        publish results to AMQP queue
        """

        msg = {'device_id': device_id,
               'measurements': measurements}

        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=json.dumps(msg),
                                   properties=pika.BasicProperties(content_type='application/json'))

    def __del__(self):
        # if self.consumer_tag:
        #    self.channel.basic_cancel(self.consumer_tag)
        self.connection.close()
