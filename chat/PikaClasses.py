# pika code for rabbitmq

import uuid
import pika


class RpcPublisher():

    def __init__(self, user, pw, ip):
        self.credentials = pika.PlainCredentials(user, pw)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            ip,
            5672,
            'socialAppHost',
            self.credentials)
            )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
                queue=self.callback_queue,
                on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message, queue):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        print("running calls publish...")
        print(message)
        self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                    ),
                body=message)
        print("while loop for processing...")
        while self.response is None:
            self.connection.process_data_events()
        return self.response
