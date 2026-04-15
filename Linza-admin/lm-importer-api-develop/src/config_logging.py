import logging
from config import LoggingConfig


def configure_logging(config: Config):
    FORMAT = '%(levelname)s - %(asctime)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=LoggingConfig.LOG_LEVEL)
