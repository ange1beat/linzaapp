import json
import re
from config import *
import logging
from urllib.parse import urlparse, urlunsplit
import datetime
import pytz
import dateparser
import requests

# import zoneinfo


def is_uuid4(string):
    return re.match(
        r"([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})$",
        string,
    )


def get_logger():
    FORMAT = "%(levelname)s - %(asctime)s - %(message)s"
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger(__name__)
    logger.setLevel(Config.LOG_LEVEL)
    return logger


logger = get_logger()


class RabbitConfigMaker:
    @staticmethod
    def main_rabbit_config():
        return {
            "host": Config.IMPORTER_RABBITMQ_HOST,
            "port": Config.IMPORTER_RABBITMQ_PORT,
            "username": Config.IMPORTER_RABBITMQ_USER,
            "password": Config.IMPORTER_RABBITMQ_PASS,
        }

    @staticmethod
    def jobqueue_rabbit_config():
        return {
            "host": Config.IMPORTER_JOBQUEUE_HOST,
            "port": Config.IMPORTER_JOBQUEUE_PORT,
            "username": Config.IMPORTER_JOBQUEUE_USER,
            "password": Config.IMPORTER_JOBQUEUE_PASS,
        }


class EventsSender:
    @staticmethod
    def prepare_0_9(item):
        ds_result = {}
        if isinstance(item, dict):
            ds_result["uid"] = str(item["uid"])
            ds_result["url"] = item["url"]
            ds_result["name"] = item["title"]
            ds_result["description"] = item["description"]
            ds_result["mapping"] = ""
            ds_result["parserType"] = item["type"]
            ds_result["isAutoCreated"] = False
            result = {}
            result["dataSourceItem"] = ds_result
        else:
            ds_result["uid"] = str(item.id)
            ds_result["url"] = item.url
            ds_result["name"] = item.title
            ds_result["description"] = item.description
            ds_result["mapping"] = ""
            ds_result["parserType"] = item.type
            ds_result["isAutoCreated"] = False
            result = {}
            result["dataSourceItem"] = ds_result
        return result

    @staticmethod
    def prepare_default_datasource_created(item):
        """send dataSourceItem FAN event to System Bus"""
        """send v.0.9"""
        ds_result = {}  # TMP for old schema
        ds_result["uid"] = str(item["id"])
        ds_result["url"] = item["url"]
        ds_result["name"] = item["title"]
        ds_result["description"] = item["description"]
        ds_result["mapping"] = ""
        ds_result["parserType"] = item["type"]
        ds_result["isAutoCreated"] = True
        result = {}
        result["dataSource"] = ds_result
        return result

    @staticmethod
    def send_0_9_default(item, producer):
        producer.connect()
        result = EventsSender.prepare_default_datasource_created(item)
        producer.push(json.dumps(result, sort_keys=True))
        producer.disconnect()

    @staticmethod
    def send_0_9_event(item, producer):
        producer.connect()
        producer.push(json.dumps(EventsSender.prepare_0_9(item), sort_keys=True))
        producer.disconnect()

    @staticmethod
    def send_0_9_deleted(data, producer):
        producer.connect()
        producer.push(json.dumps(data))
        producer.disconnect()

    @staticmethod
    def send_content_datasourceitem_updated(data, producer):
        producer.connect()
        producer.push(json.dumps(data))
        producer.disconnect()

    @staticmethod
    def send_content_parsed(data, producer):
        producer.connect()
        producer.push(json.dumps(data))
        producer.disconnect()

    @staticmethod
    def send_discover(data, producer):
        producer.connect()
        producer.push(json.dumps(data))
        producer.disconnect()

    @staticmethod
    def send_social_stats(data, producer):
        producer.connect()
        producer.push(json.dumps(data))
        producer.disconnect()

    @staticmethod
    def prepare_1_0_datasource(datasource):
        pass

    @staticmethod
    def prepare_1_0_datasourceitem(item):
        pass

    @staticmethod
    def send_1_0_datasource_created(data, producer):
        pass

    @staticmethod
    def send_1_0_datasource_updated(data, producer):
        pass

    @staticmethod
    def send_1_0_datasourcedeleted(uid):
        pass

    @staticmethod
    def send_1_0_datasourceitem_created(data, producer):
        pass

    @staticmethod
    def send_1_0_datasourceitem_updated(data, producer):
        pass

    @staticmethod
    def send_1_0_datasourceitem_daleted(uid):
        pass


def define_type(url):
    parse_result = urlparse(url)
    domain = parse_result.netloc
    base_domain = ".".join(domain.split(".")[-2:])
    if any(name == base_domain for name in ("vk.com", "vkontakte.ru")):
        type = "socialnetworks/vk"
    elif any(name == base_domain for name in ("odnoklassniki.ru", "ok.ru")):
        type = "socialnetworks/odnoklassniki"
    elif any(name == base_domain for name in ("t.me", "telegram.org")):
        type = "messengers/telegram"
    elif any(name == base_domain for name in ("facebook.com", "fb.com")):
        type = "socialnetworks/facebook"
    elif any(name == base_domain for name in ("twitter.com", "t.co")):
        type = "socialnetworks/twitter"
    elif base_domain == "instagram.com":
        type = "socialnetworks/instagram"
    elif base_domain == "youtube.com":
        type = "socialnetworks/youtube"
    elif base_domain == "livejournal.com":
        type = "socialnetworks/livejournal"
    else:
        type = "web"
    return type


def define_source_url(url):
    logging.info("defining source_url. Data provided: url: {}".format(url))
    source_url = None
    parse_result = urlparse(url)
    source_type = define_type(url)
    if source_type == "socialnetworks/facebook":
        tuple_ = (
            parse_result.scheme,
            parse_result.netloc,
            parse_result.path.split("/")[1],
            "",
            "",
        )  # TODO include redirects to profile/php?id= ???
        source_url = urlunsplit(tuple_)
    elif source_type == "socialnetworks/odnoklassniki":
        reg = re.compile(r"(\/(group|profile)\/?\d+)\/.+", re.I)
        try:
            tuple_ = (
                parse_result.scheme,
                parse_result.netloc,
                reg.search(parse_result.path)[1],
                "",
                "",
            )
            source_url = urlunsplit(tuple_)
        except Exception as e:
            logging.error("Cant get source_url from {}".format(url))
            source_url = None
    elif source_type == "socialnetworks/twitter":
        tuple_ = (
            parse_result.scheme,
            parse_result.netloc,
            parse_result.path.split("/")[1],
            "",
            "",
        )
        source_url = urlunsplit(tuple_)
    elif source_type == "messengers/telegram":
        tuple_ = (
            parse_result.scheme,
            parse_result.netloc,
            parse_result.path.split("/")[1],
            "",
            "",
        )
        source_url = urlunsplit(tuple_)
    elif source_type == "socialnetworks/livejournal":
        tuple_ = (parse_result.scheme, parse_result.netloc, "", "", "")
        source_url = urlunsplit(tuple_)
    elif source_type == "web":
        tuple_ = (parse_result.scheme, parse_result.netloc, "", "", "")
        source_url = urlunsplit(tuple_)
    return source_url


def dump_config(config_class):
    attrs = get_class_attributes(config_class)
    logging.debug(
        "{}: {}".format(config_class.__name__, json.dumps(attrs, sort_keys=True))
    )


def get_class_attributes(config_class):
    attrs = {}
    for attribute in config_class.__dict__.keys():
        if attribute[:2] != "__":
            value = getattr(config_class, attribute)
            if not callable(value):
                attrs[attribute] = value

    return attrs


def configure_logging(config):
    FORMAT = "%(levelname)s - %(asctime)s - %(message)s"
    logging.basicConfig(format=FORMAT, level=config.LEVEL)


def add_tz(date_, zone_):
    try:
        source_tz = pytz.timezone(zone_)
        # zi = zoneinfo.ZoneInfo(zone_)

        if date_.tzinfo:
            pass
        else:
            date_ = source_tz.localize(date_)
            # date_.replace(tzinfo=zi)
    except Exception as e:
        logger.warning("add_tz() cant add timezone: error: {}".format(e))

    return date_


def local_datetime_from_string(
    date_string: str, source_timezone: str, languages: list, url: str
) -> datetime:
    """a function to localize the text-view date
    input: timezone, date string
    output: datetime object localized"""
    if date_string.startswith("Неделю"):
        date_string = date_string.replace("Неделю", "1 неделю")
    with open("src/dt_config.json", "r") as f:
        data = f.read()
        dt_configs = json.loads(data)
    for dt_config in dt_configs:
        if dt_config["url"] in url:
            fmt = dt_config["dt_format"]
            if "capitalize" in dt_config:
                date_string = date_string.capitalize()
            pubDate = datetime.datetime.strptime(date_string, fmt)
            pubDate = add_tz(pubDate, source_timezone)
            return pubDate
    if date_string.endswith("Z"):
        date_string = date_string[:-1]
    try:
        pubDate = dateparser.parse(date_string, languages=languages)
    except:
        pass
    else:
        pubDate = add_tz(pubDate, source_timezone)
        return pubDate
    logging.warning("pubDate in None for 'ru'. Now trying default 'en' format")
    pubDate = dateparser.parse(date_string, languages=["en"])
    if pubDate:
        pubDate = add_tz(pubDate, source_timezone)
    return pubDate


def localize_imported_dates(date, dest_timezone):
    """Adding timezone to imported date"""
    pubDate = None
    if isinstance(date, datetime.datetime):
        dest_tz = pytz.timezone(dest_timezone)
        pubDate = dest_tz.localize(date)
    else:
        logging.error(
            "date {} is not a datetime instance. It is {}".format(date, type(date))
        )
    return pubDate


def check_vk_year(pubDate):
    """check if vk year is incorrect
    return correct date with year"""
    today_month = datetime.datetime.utcnow().month
    today_year = datetime.datetime.utcnow().year
    if all([today_month < pubDate.month, pubDate.year == today_year]):
        pubDate = pubDate.replace(year=today_year - 1)
    return pubDate


def localize_vk_dates(date, source_timezone, languages):
    """Adding tmezone to imported date"""
    pubDate = None
    source_tz = pytz.timezone(source_timezone)
    if isinstance(date, str):
        date = date.lower()
        if date.startswith("два"):
            date = date.replace("два", "2")
        elif date.startswith("три"):
            date = date.replace("три", "3")
        elif date.startswith("четыре"):
            date = date.replace("четыре", "4")
        elif date.startswith("пять"):
            date = date.replace("пять", "5")
        elif date.startswith("шесть"):
            date = date.replace("шесть", "6")
        try:
            pubDate = dateparser.parse(date, languages=languages)
        except Exception as e:
            logging.error("Cant parse date from string: {}".format(e))
        if pubDate:
            pubDate = check_vk_year(pubDate=pubDate)
            logging.info("pubDate is {}".format(pubDate))
            if pubDate.tzinfo:
                pass
            else:
                pubDate = source_tz.localize(pubDate)
    else:
        logging.error(
            "date {} is not a datetime instance. It is {}".format(date, type(date))
        )
    return pubDate


def send_telegram_alert(service_name, alert_datetime, reason):
    request_body = {
        "service_name": service_name,
        "alert_datetime": alert_datetime.isoformat(),
        "reason": reason,
    }
    try:
        requests.post(TelegramConfig.ALERT_URL, json=request_body)
        logging.debug("Telegram alert sent")
    except Exception as e:
        logging.error("Error sending telegram alert message: {}".format(e))


def parse_or_send_telegram(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            msg = "Error during parsing field: {}".format(e)
            logger.error(msg)
            send_telegram_alert(
                alert_datetime=datetime.datetime.utcnow(),
                service_name=os.getenv("SERVICE_NAME"),
                reason=msg,
            )
            return
        return result

    return inner
