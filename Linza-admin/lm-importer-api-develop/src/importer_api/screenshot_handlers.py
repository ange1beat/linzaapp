import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from importer_api.handlers import DataRequestHandler
from shared import get_logger
from tornado.escape import json_decode
from importer_api.schemas import ScreenshotSchema, ScreenshotPatchSchema, DataSourceItemSchema
from models import Screenshot, DataSourceItem
import datetime


logger = get_logger()


class ScreenshotsHandler(DataRequestHandler):
    """Creating and getting Screenshots"""

    SUPPORTED_METHODS = ["POST", "GET", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self):
        """Get all Screenshots"""
        screenshots = Screenshot.select()
        if screenshots:
            screenshot_list = []
            screenshot_schema = ScreenshotSchema()
            for screenshot in screenshots:
                screenshot_res = screenshot_schema.dump(screenshot)[0]
                screenshot_list.append(screenshot_res)
            self.set_status(200)
            response = {"statusCode": 200, "count": len(screenshot_list), "screenshot": screenshot_list}
            response = {"response": response}
            self.write(response)
        else:
            self.set_status(200)
            response = {"statusCode": 200, "screenshots": []}
            self.write(response)

    def post(self):

        raw_body = self.request.body
        try:
            body = json_decode(raw_body)
        except Exception as e:
            logger.error("POST body error: {}".format(e))
            response = {"statusCode": 400, "description": "POST body error: {}".format(e)}
            self.write(response)
            return
        if body:
            screenshot_schema = ScreenshotSchema()
            screenshot, errors = screenshot_schema.load(body)
            if len(errors) == 0:
                if not Screenshot.select().where(Screenshot.url == screenshot["url"]).exists():
                    new_screenshot = Screenshot(**screenshot)
                    new_screenshot.save(force_insert=True)
                    new_screenshot = Screenshot.select().where(Screenshot.id == new_screenshot.id).get()
                    logger.info("screenshot record created for {}".format(screenshot["url"]))
                    self.set_status(201)
                    response = {"statusCode": 201, "job": screenshot_schema.dump(new_screenshot)[0]}
                    response = {"response": response}
                    self.write(response)
                else:
                    logger.warning("screenshot record with url {} already exists".format(body["url"]))
                    self.set_status(200)
                    response = {"statusCode": 200, "description": "screenshot record with url {} already exists".format(body["url"])}
                    self.write(response)
            else:
                self.set_status(400)
                response = {"statusCode": 400, "description": "Cant create. {}".format(errors)}
                self.write(response)


class ScreenshotHandler(DataRequestHandler):

    """Getting and changing Screenshot status"""

    SUPPORTED_METHODS = ["GET", "PATCH", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'PATCH, GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self, screenshot_id):

        if Screenshot.select().where(Screenshot.id==screenshot_id).exists():
            screenshot_schema = ScreenshotSchema()
            screenshot = Screenshot.select().where(Screenshot.id == screenshot_id).get()
            self.set_status(200)
            response = {"statusCode": 200, "screenshot": screenshot_schema.dump(screenshot)[0]}
            self.write(response)
        else:
            self.set_status(200)
            response = {"statusCode": 200, "screenshot": None, "description": "screenshot does not exist"}
            self.write(response)

    def patch(self, screenshot_id):

        body = None
        raw_body = self.request.body
        try:
            body = json_decode(raw_body)
        except Exception as e:
            logger.error("POST body error: {}".format(e))
            response = {"statusCode": 400, "description": "PATCH body error: {}".format(e)}
            response = {"response": response}
            self.write(response)
        if body:
            screenshot_schema = ScreenshotSchema()
            screenshot_patch_schema = ScreenshotPatchSchema()
            clean_body, errors = screenshot_patch_schema.load(body)
            if errors:
                logger.error("Errors in patch body: {}".format(errors))
                response = {"statusCode": 400,
                            "description": "errors: {}".format(errors)}
                self.write(response)
            else:
                update_body = screenshot_patch_schema.dump(clean_body)[0]
                update_body["modified"] = datetime.datetime.utcnow()
                q = Screenshot.update(**update_body).where(Screenshot.id == screenshot_id)
                q.execute()
                updated_job = Screenshot.select().where(Screenshot.id == screenshot_id).get()
                logger.info("Job {} updated".format(screenshot_id))
                response = {"statusCode": 200,
                            "description": "Patch OK",
                            "data": screenshot_schema.dump(updated_job)[0]}
                self.write(response)


class ScreenshotScheduleHandler(DataRequestHandler):
    """get the list of urls to take screenshots. used by scheduler"""
    SUPPORTED_METHODS = ["GET", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self):
        """
        Returns list of Screenshot.urls to be taken and saved to content service
        """
        all_items = Screenshot.select().where(Screenshot.isRead==False)
        items_list = []
        for item in all_items:
            dataSourceItem = DataSourceItem.select().where(DataSourceItem.id==item.dataSourceItemUid).get()
            dsi_schema = DataSourceItemSchema()
            d = dict()
            d["dataSourceItem"] = dsi_schema.dump(dataSourceItem)[0]
            d["url"] = item.url
            items_list.append(d)
            q = Screenshot.update(
                {Screenshot.modified: datetime.datetime.utcnow(),
                 Screenshot.isRead: True}).where(Screenshot.id == item.id)
            q.execute()
        self.set_status(200)
        response = {"statusCode": 200, "count": len(items_list), "items": items_list, "errorCode": None}
        response = {"response": response}
        self.write(response)
