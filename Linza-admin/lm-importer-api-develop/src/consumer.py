import logging, pika, time


class Consumer:
    """Consumer to subscribe to jobs"""
    def __init__(self, rabbtmq_config, exchange, queue):
        self.__host = rabbtmq_config.HOST
        self.__port = rabbtmq_config.PORT
        self.__user = rabbtmq_config.USER
        self.__pass = rabbtmq_config.PASS
        self.__queue = queue
        self.__exchange = exchange
        self.__callbacks = []
        self.__tag = None
        self.__connection = None
        self.__channel = None
        self.__connected = False
        self.__stopped = False
        self.__messages = 0
        self.__callback = None

    def connect(self):
        timeout = 1
        retries = 5
        currentRetry = 0

        credentials = pika.PlainCredentials(self.__user, self.__pass)
        connection_params = pika.ConnectionParameters(self.__host,
            self.__port,
            '/',
            credentials,
            heartbeat=0,
            blocked_connection_timeout=300
        )

        while True:
            time.sleep(timeout)
            try:
                self.__connection = pika.BlockingConnection(connection_params)
                break
            except Exception as e:
                logging.warning("Cant connect to RabbitMQ: {}. Waiting {} seconds".format(e, timeout))
                self.__connection = None
                timeout = timeout + timeout * currentRetry
                currentRetry += 1
                if retries <= currentRetry:
                    ex = "Cant connect to RabbitMQ after {} retries".format(currentRetry)
                    logging.critical(ex)
                    raise Exception(ex)

        if self.__connection:
            logging.info("Connected to rabbitmq")
            self.__channel = self.__connection.channel()
            self.__channel.queue_declare(queue=self.__queue, durable=True, auto_delete=False)
            logging.info("Declared queue: {}".format(self.__queue))

    def consume(self, callback):
        self.__callback = callback
        self.connect()

        self.__channel.basic_qos(prefetch_count=1)
        self.__channel.basic_consume(self.__queue, self.process_message)
        try:
            self.__channel.start_consuming()
            logging.info("Consuming jobs...")
        except Exception as e:
            logging.error(("Error during consuming: {}".format(e)))

    def process_message(self, ch, method, properties, body):
        if self.__channel.is_open:
            try:
                self.__callback(body)
            except Exception as e:
                logging.error("Error while executing callback {}".format(e))
            self.__channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logging.warning("Channel is closed")
