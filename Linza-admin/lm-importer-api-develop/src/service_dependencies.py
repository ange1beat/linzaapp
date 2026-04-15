import logging
import time
import pika
from models import DataSourceItem
from config import DatastoreConfig
from config import ExternalRabbitConfig
from config import InternalRabbitConfig
import sys


def wait_for_datastore_database():
    connect_to_postgres()
    logging.info("Datastore database server (DB on {}:{}) is available".format(DatastoreConfig.HOST, DatastoreConfig.PORT))
    return True


def wait_for_external_rabbit():
    connect_to_rabbit(ExternalRabbitConfig)
    logging.info("External message broker (RabbitMQ on {}:{}) is available".format(ExternalRabbitConfig.HOST, ExternalRabbitConfig.PORT))
    return True


def wait_for_internal_rabbit():
    connect_to_rabbit(InternalRabbitConfig)
    logging.info("Internal message broker (RabbitMQ on {}:{}) is available".format(InternalRabbitConfig.HOST, InternalRabbitConfig.PORT))
    return True


def connect_to_postgres(timeout=1, retries=10):
    current_retry = 0
    dbavailable = False
    while dbavailable:
        time.sleep(timeout)
        try:
            sources = DataSourceItem.select().count()  # TODO: Make model parametarized
            logging.debug("DataSourceItems: {}".format(sources))
            dbavailable = True
        except Exception as e:
            timeout = timeout + timeout * current_retry
            current_retry += 1
            if current_retry == retries:
                ex = "DataStore is unavailable after {} retries. {}".format(current_retry, e)
                logging.critical(ex)
                raise Exception(ex)


def connect_to_rabbit(rabbit_config, timeout=1, retries=5):
    currentRetry = 0
    credentials = pika.PlainCredentials(rabbit_config.USER, rabbit_config.PASS)
    connection_params = pika.ConnectionParameters(
        rabbit_config.HOST,
        rabbit_config.PORT,
        '/',
        credentials,
        heartbeat=0,
        blocked_connection_timeout=300
    )
    connection_succeeded = False
    while not connection_succeeded:
        time.sleep(timeout)
        try:
            connection = pika.BlockingConnection(connection_params)
            logging.debug("Connection to rabbitmq at {}:{} established".format(rabbit_config.HOST, rabbit_config.PORT))
            connection.close()
            connection_succeeded = True
        except Exception as e:
            logging.warning("Can't connect to RabbitMQ at {}:{}. {}. Waiting {} seconds".format(rabbit_config.HOST,
                                                                                             rabbit_config.PORT,
                                                                                             e, timeout))
            timeout = timeout + timeout * currentRetry
            currentRetry += 1
            logging.info("Retries left: {}".format(retries-currentRetry))
            if currentRetry == retries:
                ex = "Cant connect to RabbitMQ at {}:{} after {} retries".format(rabbit_config.HOST,
                                                                              rabbit_config.PORT,
                                                                              currentRetry)
                logging.critical(ex)
                sys.exit("Could not connect to RabbitMQ at {}. Exiting".format(rabbit_config.HOST))
