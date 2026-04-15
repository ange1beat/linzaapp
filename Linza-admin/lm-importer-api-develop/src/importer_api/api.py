import os
import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from config import Config
from importer_api.handlers import (HealthHandler, DataSourceItemsSearchHandler,
    DataSourcesHandler, DataSourcesItemsHandler, ItemsHandler, DataSourceHandler,
    DataSourceItemHandler, SetupHandler, FilesHandler, DataSourceItemStatsHandler,
    DataSourceFullItemsHandler, DataSourcesGetByUidsHandler, DataSourcesItemsGetByUidsHandler,
    DataSourcesItemsFilterHandler, GeoIpHandler)
from importer_api.crawl_handlers import (DiscoverHandler, GetRSSLinksHandler, GetWEBLinksHandler, GetParseResultsHandler)
from importer_api.telegram_handlers import (TelegramAuthRequestHandler, TelegramSendCodeHandler, TelegramHandler,
    TelegramPhoneHandler)
from importer_api.jobs_handlers import (JobHandler, JobsHandler, JobGetByDataSourceItemUidHandler, JobTableCleanUpHandler)
from importer_api.screenshots_routes import screenshots_routes
import tornado.web
import tornado.ioloop
import tornado.routing
import tornado.httpserver
from tornado_swagger.setup import setup_swagger

static_path = os.path.join(os.path.dirname(__file__), "static")

routes = [
    tornado.routing.URLSpec(
        "/api/v1/healthCheck/?$",
        HealthHandler,
        name="api:health"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSourceItems/(?P<item_id>[0-9a-f-]+)/?$",
        DataSourceItemHandler,
        name="api:datasourceitem"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSourceItems/search/?$",
        DataSourceItemsSearchHandler,
        name="api:datasourceitemsearch"),

    tornado.routing.URLSpec(
        r"/api/v1/items",
        ItemsHandler,
        name="api:allitems"),

    tornado.routing.URLSpec(
        r"/api/v1/jobs/getByDataSourceItemUid",
        JobGetByDataSourceItemUidHandler,
        name="api:jobgetbydatasourceitemuid"),

    tornado.routing.URLSpec(
        r"/api/v1/jobs/?$",
        JobsHandler,
        name="api:jobs"),

    tornado.routing.URLSpec(
        "/api/v1/telegram/authRequest/?$",
        TelegramAuthRequestHandler,
        name="api:telegramAuthRequest"),

    tornado.routing.URLSpec(
        "/api/v1/telegram/sendCode/?$",
        TelegramSendCodeHandler,
        name="api:telegramSendCode"),

    tornado.routing.URLSpec(
        "/api/v1/telegram/?$",
        TelegramHandler,
        name="api:telegram"),

    tornado.routing.URLSpec(
        "/api/v1/telegram/(?P<phone>.{0,11})",
        TelegramPhoneHandler,
        name="api:telegramPhone"),

    tornado.routing.URLSpec(
        r"/api/v1/discover/?.*",
        DiscoverHandler,
        name="api:discover"),

    tornado.routing.URLSpec(
        r"/api/v1/getRSSLinks/?.*",
        GetRSSLinksHandler,
        name="api:getRSSLinks"),

    tornado.routing.URLSpec(
        r"/api/v1/getWEBLinks/?",
        GetWEBLinksHandler,
        name="api:getWEBLinks"),

    tornado.routing.URLSpec(
        r"/api/v1/getParseResults/?",
        GetParseResultsHandler,
        name="api:getParseResults"),

    tornado.routing.URLSpec(
        r"/api/v1/setup/?$",
        SetupHandler,
        name="api:setup"),

    tornado.routing.URLSpec(
        r"/api/v1/files/?$",
        FilesHandler,
        name="api:files"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/getByUids/?",
        DataSourcesGetByUidsHandler,
        name="api:datasourcesGetByUids"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSourcesItems/getByUids/?",
        DataSourcesItemsGetByUidsHandler,
        name="api:datasourcesitemsGetByUids"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSourcesItems/?$",
        DataSourcesItemsFilterHandler,
        name="api:datasourcesitemsfilter"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/(?P<datasource_id>[0-9a-f-]+)/?$",
        DataSourceHandler,
        name="api:datasource"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/fullItems/?$",
        DataSourceFullItemsHandler,
        name="api:fullItems"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/(?P<datasource_id>[0-9a-f-]+)/dataSourceItems/?$",
        DataSourcesItemsHandler,
        name="api:datasourceitems"),

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/?$",
        DataSourcesHandler,
        name="api:dataSources"),    

    tornado.routing.URLSpec(
        r"/api/v1/dataSources/(?P<datasource_id>[0-9a-f-]+)/dataSourceItems/(?P<item_id>[0-9a-f-]+)/stats/?$",
        DataSourceItemStatsHandler,
        name="api:datasourceitemstats"),
    
    tornado.routing.URLSpec(
        r"/api/v1/jobs/cleanup/?$",
        JobTableCleanUpHandler,
        name="api:jobscleanup"),

    tornado.routing.URLSpec(
        r"/api/v1/jobs/(?P<job_id>[0-9a-f-]+)/?$",
        JobHandler,
        name="api:job"),    

    tornado.routing.URLSpec(
        r"/api/v1/geoIP",
        GeoIpHandler,
        name="api:geoip"),
]

routes.extend(screenshots_routes)


def get_routes():
    return routes


def get_application():
    setup_swagger(routes)
    return tornado.web.Application(
        routes,
        # {"static_path": os.path.join(os.path.dirname(__file__), "static")}
    )


def main():
    app = get_application()
    app.listen(Config.IMPORTER_API_PORT)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
