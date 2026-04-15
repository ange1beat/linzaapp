import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from importer_api.handlers import BaseHandler
from shared import get_logger
from tornado.escape import json_decode
from models import Telegram
from importer_api.schemas import TelegramSchema
import uuid


logger = get_logger()


class TelegramPhoneHandler(BaseHandler): 
    SUPPORTED_METHODS = ["GET", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self, phone):        
        """Get phone info.
        ---
        description: Get phone info.
        parameters:
        -   name: phone
            in: path
            description: phone number
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        phone:
                            type: string
                            description: phone
                        code:
                            type: string
                            description: code
                        auth_request:
                            type: string
                            description: auth_request
                        datetime:
                            type: string
                            description: datetime
        """
        response = dict()
        # if self.get_argument("phone"):
        # phone = self.get_query_argument("phone")
        if Telegram.select().where(Telegram.phone == phone).exists():
            tlg = Telegram.select().where(Telegram.phone == phone).get()
            tlg_schema = TelegramSchema()
            result, errors = tlg_schema.dump(tlg)
            if not errors:
                response = result
            else:
                logger.warning("Phone {} not exists".format(errors))
        self.set_status(200)
        self.write(response)


class TelegramHandler(BaseHandler):    
    

    SUPPORTED_METHODS = ["GET", "POST", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def post(self):        
        """Add new number.
        ---
        description: Add new number.
        parameters:
        -   name: phone
            in: path
            description: phone number
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        statusCode:
                            type: string
                            description: need_auth
                        description:
                            type: string
                            description: description
                        errorCode:
                            type: string
                            description: errorCode
        """
        body = None
        try:
            body = json_decode(self.request.body)
        except Exception as e:
            logger.error("Error getting request body: ", e)
            self.set_status(400)
            response = {"statusCode": 400, "description": "Error getting POST request body: {}".format(e),
                        "errorCode": None}
            response = {"response": response}
            self.write(response)
        if body:
            phone = body["phone"]
            tlg_schema = TelegramSchema()
            if not Telegram.select().where(Telegram.phone==phone).exists():
                new_item, errors = tlg_schema.load({"uid": str(uuid.uuid4()), "phone": phone})
                print(new_item)
                if not errors:
                    tlg_record = Telegram(**new_item)
                    tlg_record.save(force_insert=True)
                    new_tlg = Telegram.select().where(Telegram.phone==phone).get()
                    self.set_status(201)
                    self.write(tlg_schema.dump(new_tlg)[0])
                else:
                    logger.error("Error: {}".format(errors))
                    self.set_status(400)
                    self.write(errors)
            else:
                logger.warning("Such phone already exists: {}".format(phone))
                self.set_status(400)
                self.write("Phone already exists: {}".format(phone))

    def get(self):        
        """Get list of added phones.
        ---
        description: Get list of added phones.       
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        count:
                            type: int
                            description: need_auth
                        data:
                            type: string
                            description: list of phones                       
        """
        q = Telegram.select()
        tlg_schema = TelegramSchema()
        result_list = list()
        response = dict()
        for item in q:
            result, errors = tlg_schema.dump(item)
            if not errors:
                result_list.append(result)

            else:
                logger.error("Errors: {}".format(errors))
        response = {"count": len(result_list), "data": result_list}
        self.set_status(200)
        self.write(response)


class TelegramAuthRequestHandler(BaseHandler): 
    SUPPORTED_METHODS = ["GET", "POST", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self):
        """Get account status and request auth in telegram.
        ---
        description: Get account status and request auth in telegram.
        parameters:
        -   name: phone
            in: path
            description: phone number
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        need_auth:
                            type: string
                            description: need_auth
                        code:
                            type: string
                            description: code
                        phone:
                            type: string
                            description: phone
        """
        phone = self.get_argument("phone", None)
        record = None
        if phone:
            try:
                record = Telegram.select().where(Telegram.phone == phone).get()
            except Exception as e:
                logger.error("No such phone in DB: {}: {}".format(phone, e))
            if record:
                response = {"need_auth": record.auth_request,
                            "code": record.code,
                            "phone": phone}
                self.set_status(200)
                self.write(response)

    def post(self):        
        """change the auth_request to True.
        ---
        description: change the auth_request to True.
        parameters:
        -   name: phone
            in: body
            description: phone number
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        statusCode:
                            type: string
                            description: statusCode
                        description:
                            type: string
                            description: description
                        errorCode:
                            type: string
                            description: errorCode
        """
        body = None
        try:
            body = json_decode(self.request.body)
        except Exception as e:
            logger.error("Error getting request body: ", e)
            self.set_status(400)
            response = {"statusCode": 400, "description": "Error getting POST request body: {}".format(e),
                        "errorCode": None}
            response = {"response": response}
            self.write(response)
        if body:
            phone = body["phone"]
            if Telegram.select().where(Telegram.phone==phone).exists():
                q = (Telegram.update({
                    Telegram.auth_request: True
                }).where(Telegram.phone == phone))
                q.execute()
                tlg = Telegram.select().where(Telegram.phone==phone).get()

                self.set_status(200)
                self.write({"phone": tlg.phone,
                            "code": tlg.code,
                            "auth_request": tlg.auth_request})
            else:
                logger.warning("Phone does not exist: {}".format(phone))
                self.set_status(400)
                self.write("Phone does not exist: {}".format(phone))


class TelegramSendCodeHandler(BaseHandler):
    SUPPORTED_METHODS = ["POST", "OPTIONS"]
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def post(self):
        """Send code to Telegram.
        ---
        description: Send code to Telegram.
        parameters:
        -   name: phone
            in: body
            description: phone number
            required: true
            type: string
        responses:
            200:
                description: Success                
                schema:
                    type: object
                    properties:
                        statusCode:
                            type: string
                            description: statusCode
                        description:
                            type: string
                            description: description
                        errorCode:
                            type: string
                            description: errorCode
        """
        body = None
        try:
            body = json_decode(self.request.body)
        except Exception as e:
            logger.error("Error getting request body: ", e)
            self.set_status(400)
            response = {"statusCode": 400, "description": "Error getting POST request body: {}".format(e),
                        "errorCode": None}
            response = {"response": response}
            self.write(response)
        if body:
            logger.info("body: {}".format(body))
            phone = body["phone"]
            code = body["code"]
            if Telegram.select().where(Telegram.phone == phone).exists():
                q = (Telegram.update({
                    Telegram.code: code,
                    Telegram.auth_request: False
                }).where(Telegram.phone == phone))
                q.execute()
                tlg = Telegram.select().where(Telegram.phone==phone).get()
                self.set_status(200)
                self.write({"phone": tlg.phone,
                            "code": tlg.code,
                            "auth_request": tlg.auth_request})
            else:
                logger.warning("Phone does not exist: {}".format(phone))
                self.set_status(400)
                self.write("Phone does not exist: {}".format(phone))
        else:
            logger.warning("Body: {}".format(body))
            self.set_status(400)
            self.write("Errors in body")

