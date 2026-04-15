import pika
import logging


class Producer(object):

    def __init__(self, queue, config, exchange="", type_='direct', routing_key=""):
        self.__host = config["host"]
        self.__port = config["port"]
        self.__user = config["username"]
        self.__pass = config["password"]
        self.__exchange = exchange
        self.__exchange_type = type_
        self.__queue = queue
        self.__routing_key = routing_key
        self.__callbacks = []
        self.__tag = None
        self.__connection = None
        self.__channel = None
        self.__connected = False
        self.__stopped = False
        self.__messages = 0

    def connect(self):
        credentials = pika.PlainCredentials(self.__user, self.__pass)
        try:
            self.__connection = pika.BlockingConnection(pika.ConnectionParameters(self.__host, self.__port, '/',
                                                                                  credentials, heartbeat=0,
                                                                                  blocked_connection_timeout=300))
            self.__channel = self.__connection.channel()

            self.__channel.queue_declare(queue=self.__queue, durable=True)
            if self.__exchange != "":
                self.__channel.exchange_declare(exchange=self.__exchange, exchange_type=self.__exchange_type,
                                                durable=True)
                self.__channel.queue_bind(exchange=self.__exchange, queue=self.__queue, routing_key=self.__routing_key)
            else:
                self.__routing_key = self.__queue

        except Exception as e:
            logging.error("Cant connect to RabbitMQ: {}".format(e))
            self.__channel = None

    def push(self, item):
        if self.__connection:
            self.__channel.basic_publish(
                exchange=self.__exchange,
                routing_key=self.__routing_key,
                body=item,
                properties=pika.BasicProperties(
                    delivery_mode=2)
            )
        else:
            logging.error("No rabbitmq channel to push data.")

    def disconnect(self):
        if self.__channel.is_open:
            self.__channel.close()
