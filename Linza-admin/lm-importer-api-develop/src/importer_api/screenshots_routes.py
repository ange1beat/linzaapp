import tornado.routing
from importer_api.screenshot_handlers import (ScreenshotHandler, ScreenshotsHandler, ScreenshotScheduleHandler)


screenshots_routes = [
    tornado.routing.URLSpec(
        "/api/v1/screenshots/?$",
        ScreenshotsHandler,
        name="api:screenshots"),
    tornado.routing.URLSpec(
        "/api/v1/screenshots/(?P<screenshot_id>[0-9a-f-]+)/?$",
        ScreenshotHandler,
        name="api:screenshot"),
    tornado.routing.URLSpec(
        "/api/v1/screenshots/schedule",
        ScreenshotScheduleHandler,
        name="api:screenshotschedule"),
    ]
