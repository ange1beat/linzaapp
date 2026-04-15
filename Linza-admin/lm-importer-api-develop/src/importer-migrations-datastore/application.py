import peeweedbevolve  # must be 1st
import os
import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
import time
import datetime
import uuid
from config import Config
from models import *
from producer import Producer
from shared import EventsSender, RabbitConfigMaker, get_logger


logger = get_logger()


def create_tables_datastore():
    if datastore.is_closed():
        datastore.connect()
    datastore.evolve(interactive=False)
    if not datastore.is_closed():
        datastore.close()

#
# default_telegram_user = {
#     "phone": os.getenv("PHONE_NUMBER"),
#     "auth_request": False,
#     "code": 0
# }

defaultDataSourceItem = {
    "created": str(datetime.datetime.utcnow()),
    "modified": None,
    "id": "070582cc-d484-4a82-b8bc-0aa447447de3",
    "title": Config.DEFAULT_DATASOURCEITEM_TITLE,
    "description": "defaultDescription",
    "iconUri": "",    
    "url": "",
    "type": "default",
    "updateInterval": 3600,
    "config": {},
    "account": {},
    "isAutoCreated": True,
    "isActive": False,
    "timezone": "UTC",
    "updated": str(datetime.datetime.utcnow())
}


n = 5
while True:
    try:
        create_tables_datastore()
        logger.info("Tables OK")
        break
    except Exception as e:
        logger.warning("Can't connect to DB {}: {}".format("Importer-DataStore", e))
        logger.info("Waiting for Postgres..")
        time.sleep(n)
        if n < 10:
            n += 1

# if Telegram.select().where(Telegram.phone == os.getenv("PHONE_NUMBER")).exists():
#     pass
# else:
#     telegram = Telegram.create(**default_telegram_user)
#     logger.info("Default Telegram User created")

logger.info("Creating default dataSourceItem")
if all([DataSourceItem.select().where(DataSourceItem.id == uuid.UUID(defaultDataSourceItem["id"])).exists()]):
    logger.info("DefaultDataSourceItem exist")
    exit(0)
else:
    with datastore.atomic() as tx:
        health = None
        try:
            health = Health.select()
        except Exception as e:
            logger.error("Cant get Health record")
        if len(health) > 0:
            pass
        else:
            Health.create(name="HealthCheck is OK", status="OK")
        
        new_item = DataSourceItem.create(**defaultDataSourceItem)
        """send 1.0"""
        """end of 1.0"""
        logger.info("DefaultDataSourceItem created")
        msg_sent = True;
#        t = 10
#        while not msg_sent:
#            try:
#                """send dataSourceItem FAN event to System Bus"""
#                """send v.0.9"""
#                logger.info("Sending Default DataSource Created message")
#                producer = Producer(exchange=Config.IMPORTER_DATASOURCE_CREATED_EXCHANGE_0_9,
#                                    queue=Config.IMPORTER_DATASOURCE_CREATED_QUEUE_0_9,
#                                    routing_key=Config.IMPORTER_DATASOURCE_CREATED_ROUTING_KEY_0_9,
#                                    config=RabbitConfigMaker.main_rabbit_config()
#                                    )
#                EventsSender.send_0_9_default(item=defaultDataSourceItem, producer=producer)
#                logger.info("Default message sent")
#                msg_sent = True
#            except Exception as e:
#                # logger.warning("Transaction rolled back")
#                logger.error("Cant send message: {}".format(e))
#                time.sleep(t)
#                if t < 30:
#                    t += 10

        if msg_sent:
            tx.commit()
        else:
            tx.rollback()
