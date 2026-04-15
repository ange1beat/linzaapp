import os


class LoggingConfig:
    LEVEL = os.getenv("LOG_LEVEL", "INFO")


class ContentParsedProducerConfig:
    EXCHANGE = os.getenv("CONTENT_PARSED_EXCHANGE", "content")
    QUEUE = os.getenv("CONTENT_PARSED_QUEUE", "contentParsed")
    ROUTING_KEY = os.getenv("CONTENT_PARSED_ROUTING_KEY", "contentParsed")


class DatastoreConfig:
    HOST = os.getenv("DATASTORE_HOST", "importer-datastore")
    PORT = os.getenv("DATASTORE_PORT", 5432)
    USER = os.getenv("DATASTORE_USER", "pguser")
    PASS = os.getenv("DATASTORE_PASS", "PLoAj1DB")
    DBNAME = os.getenv("DATASTORE_DBNAME", "importer-datastore")


class ExternalRabbitConfig:
    HOST = os.getenv("IMPORTER_RABBITMQ_HOST", "rabbitmq")
    PORT = os.getenv("IMPORTER_RABBITMQ_PORT", 5672)
    USER = os.getenv("IMPORTER_RABBITMQ_USER", "guest")
    PASS = os.getenv("IMPORTER_RABBITMQ_PASS", "guest")


class InternalRabbitConfig:
    HOST = os.getenv("IMPORTER_JOBQUEUE_HOST", "importer-jobqueue")
    PORT = os.getenv("IMPORTER_JOBQUEUE_PORT", 5672)
    USER = os.getenv("IMPORTER_JOBQUEUE_USER", "guest")
    PASS = os.getenv("IMPORTER_JOBQUEUE_PASS", "guest")


class JobConsumerConfig:
    EXCHANGE = os.getenv("JOBQUEUE_EXCHANGE", "")

class Config:

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TOR_PROXY_URL = os.getenv("TOR_PROXY_URL", "http://tor-proxy:8118")

    IMPORTER_API_HOST = os.getenv("IMPORTER_API_HOST", "importer-api")
    # IMPORTER_API_HOST = os.getenv("IMPORTER_API_HOST", "localhost")

    IMPORTER_API_PORT = os.getenv("IMPORTER_API_PORT", 80)

    CONTENT_API_HOST = os.getenv("CONTENT_API_HOST", "content-api")
    CONTENT_API_PORT = os.getenv("CONTENT_API_PORT", 80)
    CONTENT_API_SEARCH_URL = os.getenv("CONTENT_API_SEARCH_URL", "http://content-api/api/v1/contents")
    CONTENT_SCREENSHOT_API = os.getenv("CONTENT_SCREENSHOT_API", "http://content-api/api/v1/screenshots")

    IMPORTER_DATASTORE_HOST = os.getenv("IMPORTER_DATASTORE_HOST", "importer-datastore")
    # IMPORTER_DATASTORE_HOST = os.getenv("IMPORTER_DATASTORE_HOST", "localhost")
    IMPORTER_DATASTORE_PORT = os.getenv("IMPORTER_DATASTORE_PORT", 5432)
    # IMPORTER_DATASTORE_PORT = os.getenv("IMPORTER_DATASTORE_PORT", 5433)
    IMPORTER_DATASTORE_DBNAME = os.getenv("IMPORTER_DATASTORE_DBNAME", "importer-datastore")
    IMPORTER_DATASTORE_DBUSER = os.getenv("IMPORTER_DATASTORE_DBUSER", "pguser")
    IMPORTER_DATASTORE_DBPASS = os.getenv("IMPORTER_DATASTORE_DBPASS", "PLoAj1DB")

    IMPORTER_FILESTORE_HOST = os.getenv("IMPORTER_FILESTORE_HOST", "importer-filestore")
    IMPORTER_FILESTORE_PORT = os.getenv("IMPORTER_FILESTORE_PORT", 5432)
    IMPORTER_FILESTORE_DBNAME = os.getenv("IMPORTER_FILESTORE_DBNAME", "importer-filestore")
    IMPORTER_FILESTORE_DBUSER = os.getenv("IMPORTER_FILESTORE_DBUSER", "pguser")
    IMPORTER_FILESTORE_DBPASS = os.getenv("IMPORTER_FILESTORE_DBPASS", "Gs2LsdIG")

    IMPORTER_JOBQUEUE_HOST = os.getenv("IMPORTER_JOBQUEUE_HOST", "importer-jobqueue")
    IMPORTER_JOBQUEUE_PORT = os.getenv("IMPORTER_JOBQUEUE_PORT", 5672)
    IMPORTER_JOBQUEUE_EXCHANGE = os.getenv("IMPORTER_JOBQUEUE_EXCHANGE", "")
    IMPORTER_JOBQUEUE_USER = os.getenv("IMPORTER_JOBQUEUE_USER", "guest")
    IMPORTER_JOBQUEUE_PASS = os.getenv("IMPORTER_JOBQUEUE_PASS", "guest")

    IMPORTER_RABBITMQ_HOST = os.getenv("IMPORTER_RABBITMQ_HOST", "rabbitmq")
    IMPORTER_RABBITMQ_PORT = os.getenv("IMPORTER_RABBITMQ_PORT", 5672)
    IMPORTER_RABBITMQ_USER = os.getenv("IMPORTER_RABBITMQ_USER", "guest")
    IMPORTER_RABBITMQ_PASS = os.getenv("IMPORTER_RABBITMQ_PASS", "guest")

    # IMPORTER_RABBITMQ_QUEUE_NAME = os.getenv("IMPORTER_RABBITMQ_QUEUE_NAME", "parsing_queue")

    IMPORTER_DATASOURCE_CREATED_EXCHANGE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_CREATED_EXCHANGE", "content")
    IMPORTER_DATASOURCE_CREATED_QUEUE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_CREATED_QUEUE",
                                                      "graphConsumer_dataSourceCreatedQueue")
    IMPORTER_DATASOURCE_CREATED_ROUTING_KEY_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_CREATED_ROUTING_KEY",
                                                            "dataSourceCreated_v09")

    IMPORTER_DATASOURCE_UPDATED_EXCHANGE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_UPDATED_EXCHANGE", "content")
    IMPORTER_DATASOURCE_UPDATED_QUEUE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_UPDATED_QUEUE",
                                                      "graphConsumer_dataSourceUpdatedQueue")
    IMPORTER_DATASOURCE_UPDATED_ROUTING_KEY_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_UPDATED_ROUTING_KEY",
                                                            "dataSourceUpdated_v09")

    IMPORTER_DATASOURCE_DELETED_EXCHANGE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_DELETED_EXCHANGE", "content")
    IMPORTER_DATASOURCE_DELETED_QUEUE_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_DELETED_QUEUE",
                                                      "graphConsumer_dataSourceDeletedQueue")
    IMPORTER_DATASOURCE_DELETED_ROUTING_KEY_0_9 = os.getenv("IMPORTER_FAN_DATASOURCE_DELETED_ROUTING_KEY",
                                                            "dataSourceDeleted_v09")

    IMPORTER_DATASOURCEITEM_CREATED = os.getenv("IMPORTER_FAN_DATASOURCEITEM_CREATED", "dataSourceItemCreated")
    IMPORTER_DATASOURCEITEM_UPDATED = os.getenv("IMPORTER_FAN_DATASOURCEITEM_UPDATED", "dataSourceItemUpdated")
    IMPORTER_DATASOURCEITEM_DELETED = os.getenv("IMPORTER_FAN_DATASOURCEITEM_DELETED", "dataSourceItemDeleted")

    IMPORTER_SOCIAL_STATS_UPDATE_INTERVAL = os.getenv("IMPORTER_SOCIAL_STATS_UPDATE_INTERVAL", 80)
    IMPORTER_SOCIAL_STATS_EXCHANGE = os.getenv("IMPORTER_SOCIAL_STATS_EXCHANGE", "socialStats")
    IMPORTER_SOCIAL_STATS_ROUTING_KEY = os.getenv("IMPORTER_SOCIAL_STATS_EXCHANGE", "")
    SOCIAL_STATS_QUEUES = [
        "social_stats/twitter",
        "social_stats/facebook",
        "social_stats/odnoklassniki",
        "social_stats/livejournal",
        "social_stats/vk"
    ]

    IMPORTER_RSS_API_HOST = os.getenv("IMPORTER_RSS_API_HOST", "importer-rss-api")
    IMPORTER_RSS_API_PORT = os.getenv("IMPORTER_RSS_API_PORT", 5000)

    IMPORTER_ATOM_API_HOST = os.getenv("IMPORTER_ATOM_API_HOST", "importer-atom-api")
    IMPORTER_ATOM_API_PORT = os.getenv("IMPORTER_ATOM_API_PORT", 5001)

    TYPES = [
        "rss_crawl",
        "rss",
        "atom",
        "web",
        "socialnetworks/vk",
        "socialnetworks/odnoklassniki",
        "socialnetworks/twitter",
        "socialnetworks/instagram",
        "socialnetworks/youtube",
        "socialnetworks/facebook",
        "messengers/telegram",
        "socialnetworks/livejournal",
        "importer-test",
        "screenshot",
    ]

    KNOWN_SOCIAL_NETWORKS = [
      "vk.com",
      "vkontakte.ru",
      "facebook.com",
      "fb.com",
      "instagram.com",
      "youtube.com",
      "ok.ru",
      "odnoklassniki.ru",
      "twitter.com",
      "t.co",
      "t.me",
      "telegram.org",
      "livejournal.com"
    ]

    SOCIAL_TYPES = [
        "socialnetworks/vk",
        "socialnetworks/odnoklassniki",
        "socialnetworks/twitter",
        "socialnetworks/instagram",
        "socialnetworks/youtube",
        "socialnetworks/facebook",
        "messengers/telegram",
        "socialnetworks/livejournal",
    ]

    IMPORTER_DISCOVER_WORKER_EXCHANGE = os.getenv("IMPORTER_DISCOVER_WORKER_EXCHANGE", "discover")
    IMPORTER_DISCOVER_WORKER_QUEUE = os.getenv("IMPORTER_DISCOVER_WORKER_QUEUE", "discover")
    IMPORTER_DISCOVER_WORKER_ROUTING_KEY = os.getenv("IMPORTER_DISCOVER_WORKER_ROUTING_KEY", "")

    CONTENT_PARSED_EXCHANGE = os.getenv("CONTENT_PARSED_EXCHANGE", "content")
    CONTENT_PARSED_QUEUE = os.getenv("CONTENT_PARSED_QUEUE", "contentParsed")
    CONTENT_PARSED_ROUTING_KEY = os.getenv("CONTENT_PARSED_ROUTING_KEY", "contentParsed")

    CONTENT_DATASOURCE_ITEM_UPDATED_EXCHANGE = os.getenv("CONTENT_DATASOURCE_ITEM_UPDATED_EXCHANGE", "content")
    CONTENT_DATASOURCE_ITEM_UPDATED_QUEUE = os.getenv("DISCOVER_CONTENT_UPDATED", "contentDataSourceItemUpdated")
    CONTENT_DATASOURCE_ITEM_UPDATED_ROUTING_KEY = os.getenv("DISCOVER_CONTENT_UPDATED", "contentDataSourceItemUpdated")

    IMPORTER_SCHEDULER_UPDATE_INTERVAL = os.getenv("IMPORTER_SCHEDULER_UPDATE_INTERVAL", 60)

    DEFAULT_DATASOURCEITEM_UID = "070582cc-d484-4a82-b8bc-0aa447447de3"
    DEFAULT_DATASOURCEITEM_TITLE = os.getenv("DEFAULT_DATASOURCEITEM_TITLE", "defaultDataSourceItem")

    DESTINATION_TIMEZONE = os.getenv("DESTINATION_TIMEZONE", "Europe/Moscow")

    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    JOB_CLEANUP_ENDPOINT = "api/v1/jobs/cleanup"
    JOB_CLEANUP_DAYS = 7
    
    GEOIP_API_KEY = os.getenv("GEOIP_API_KEY", "ee5edcfd13214163970c1048e642e72f")
