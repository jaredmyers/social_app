# pika code for rabbitmq

import uuid
import pika
from chat.db_accessor_methods import accessor_methods


class RpcPublisher():
    """
    A class for sending messages to a specific rabbitMQ queue
    """

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


class RunSubscriber():

    def __init__(self, user, pw, ip):
        self.credentails = pika.PlainCredentails(user, pw)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            ip,
            5672,
            'socialAppHost',
            self.credentails)
            )

        self.channel = None

    def rpc_subscribe(self, queue):

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)

        def send_to_accessor_methods(body, queue):
            response = accessor_methods(body, queue)
            return response

        def on_request(ch, method, props, body):
            print(" [.] message(%s)" % body)
            response = send_to_accessor_methods(body, queue)

            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(
                                correlation_id=props.correlation_id
                             ),
                             body=response)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=queue, on_message_callback=on_request)
        print(" [x] awaiting rpc request..")
        self.channel.start_consuming()
