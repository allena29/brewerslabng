import json
import traceback
import pika
import time

import blng.LogHandler as LogHandler

"""
This class provides an interface to send data to a rabitmq based queue.
"""


class Common:

    RABBIT_MQ_SERVER = '192.168.1.28'
    RABBIT_MQ_USER = 'beerng'
    RABBIT_MQ_PASS = 'beerng'

    def __init__(self, exchange='default', log_component=''):
        self.log = LogHandler.LogHandler(log_component + self.RABBIT_TYPE)
        self.connection = None
        self.channel = None
        self.exchange = exchange

    def __del__(self):
        try:
            self.connection.close()
        except Exception:
            pass

    def _open_connection(self):
        """
        Open a connection to RabitMQ for us to produce messges on
        """
        self.log.info('Opening conneciton to RabbitMQ: %s' % (self.RABBIT_MQ_SERVER))
        credentials = pika.PlainCredentials(self.RABBIT_MQ_USER, self.RABBIT_MQ_PASS)
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.RABBIT_MQ_SERVER, credentials=credentials)
            )
        except pika.exceptions.AMQPConnectionError:
            self.log.error('Unable to connect to RabitMQ')
            return False
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, exchange_type='direct')
        self.log.info('Exchange Declared: %s' % (self.exchange))
        return True


class Producer(Common):

    RABBIT_TYPE = 'Producer'

    def send_message(self, msg, port=None, app='unknown-app'):
        if not self.channel:
            if not self._open_connection():
                self.log.error('Unable to open a connection to produce messages')
                return False

        controlMessage = msg
        controlMessage['_operation'] = app
        try:
            self.log.debug('Sending message: %s' % (controlMessage))
            self.channel.basic_publish(exchange=self.exchange, routing_key=str(port),
                                       body=json.dumps(controlMessage))
        except pika.exceptions.StreamLostError:
            self.log.error('Stream Lost Error')
            self.connection = None
            self.channel = None
        except Exception:
            self.log.error('Unhandlded error: %s' % (traceback.format_exc()))
            self.connection = None
            self.channel = None
            print('a error')


class Consumer(Common):

    RABBIT_TYPE = 'Consumer'

    def register(self, callback, port):
        """
        Open a socket a listen for data in 1200 byte chunks.
        Fire the callback each time
        """
        self._open_connection()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=self.exchange, queue=self.queue_name, routing_key=str(port))

        def mq_callback(ch, method, properties, body):
            callback(json.loads(body))

        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=mq_callback, auto_ack=True)
        self.log.info('Registered Callback: %s for %s' % (callback, self.queue_name))
        self.channel.start_consuming()
