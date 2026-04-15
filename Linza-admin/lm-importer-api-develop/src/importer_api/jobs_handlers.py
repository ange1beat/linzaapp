import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from importer_api.handlers import DataRequestHandler
from shared import get_logger
from tornado.escape import json_decode
from importer_api.schemas import JobSchema, JobPatchSchema
from models import Job
import datetime
from config import Config


logger = get_logger()

class JobGetByDataSourceItemUidHandler(DataRequestHandler):
    """Endpoint to get last job result. Modified field used to define latest date"""
    SUPPORTED_METHODS = ["GET", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self):       
        """Get last job for given DataSourceItemUid
        ---
        description: Get last job for given DataSourceItemUid
        parameters:
        -   name: uid
            in: query
            description: uid
            required: true
            type: string        
        responses:
            200:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        job:
                            type: object
                            description: job
        """
        datasource_item_uid = self.get_argument("uid", default=None)
        if datasource_item_uid:
            if Job.select().where(Job.dataSourceItemUid == datasource_item_uid).exists():
                job_schema = JobSchema()
                job = Job.select().where(
                    Job.dataSourceItemUid == datasource_item_uid).order_by(
                    Job.modified.desc()).get()
                self.set_status(200)
                response = {"statusCode": 200, "job": job_schema.dump(job)[0]}
                self.write(response)
            else:
                self.set_status(200)
                response = {"statusCode": 200, "job": None, "description": "Job does not exist"}
                self.write(response)

class JobsHandler(DataRequestHandler):
    """Creating and getting Jobs"""

    SUPPORTED_METHODS = ["POST", "GET", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self):        
        """Get all Jobs
        ---
        description: Get all Jobs
        responses:
            200:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        count:
                            type: integer
                            description: count                      
                        jobs:
                            type: array
                            description: jobs list                            
        """
        jobs = Job.select()
        if jobs:
            job_list = []
            job_schema = JobSchema()
            for job in jobs:
                job_res = job_schema.dump(job)[0]
                job_list.append(job_res)
            self.set_status(200)
            response = {"statusCode": 200, "count": len(job_list), "jobs": job_list}
            response = {"response": response}
            self.write(response)
        else:
            self.set_status(200)
            response = {"statusCode": 200, "jobs": []}
            self.write(response)

    def post(self):
        """Create job.
        ---
        description: Create job.
        parameters:
        -   name: dataSourceItemUid
            in: path
            description: dataSourceItemUid
            required: true
            type: string
        -   name: read_by_worker
            in: path
            description: read_by_worker
            required: false
            type: string
        -   name: done_by_worker
            in: body
            description: done_by_worker
            required: false
            type: string
        -   name: success
            in: body
            description: success
            required: false
            type: boolean
        -   name: fail_description
            in: body
            description: fail_description
            required: false
            type: string
        -   name: proxy_used
            in: body
            description: proxy_used
            required: false
            type: string        
        responses:
            201:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        job:
                            type: object
                            description: job
        """
        raw_body = self.request.body
        try:
            body = json_decode(raw_body)
        except Exception as e:
            logger.error("POST body error: {}".format(e))
            response = {"statusCode": 400, "description": "POST body error: {}".format(e)}
            self.write(response)
            return
        if body:
            job_schema = JobSchema()
            job, errors = job_schema.load(body)
            if len(errors) == 0:
                new_job = Job(**job)
                if not Job.select().where(Job.id == body["uid"]).exists():
                    new_job.save(force_insert=True)
                    new_job = Job.select().where(Job.id == new_job.id).get()
                    self.set_status(201)
                    response = {"statusCode": 201, "job": job_schema.dump(new_job)[0]}
                    response = {"response": response}
                    self.write(response)
                else:
                    logger.warning("Job with uid {} already exists".format(body["uid"]))
                    self.set_status(400)
                    response = {"statusCode": 400, "description": "Job with uid {} already exists".format(body["uid"])}
                    self.write(response)
            else:
                self.set_status(400)
                response = {"statusCode": 400, "description": "Cant create. {}".format(errors)}
                self.write(response)


class JobHandler(DataRequestHandler):

    """Getting and changing Job status"""

    SUPPORTED_METHODS = ["GET", "PATCH", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'PATCH, GET, OPTIONS')
        self.set_status(204)
        self.finish()

    def get(self, job_id):
        """Get job information
        ---
        description: Get job information
        parameters:
        -   name: job_id
            in: path
            description: job_id
            required: true
            type: string        
        responses:
            200:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        job:
                            type: object
                            description: job
        """
        if Job.select().where(Job.id==job_id).exists():
            job_schema = JobSchema()
            job = Job.select().where(Job.id == job_id).get()
            self.set_status(200)
            response = {"statusCode": 200, "job": job_schema.dump(job)[0]}
            self.write(response)
        else:
            self.set_status(200)
            response = {"statusCode": 200, "job": None, "description": "Job does not exist"}
            self.write(response)

    def patch(self, job_id):
        """Patch job
        ---
        description: Patch job
        parameters:
        -   name: job_id
            in: path
            description: job_id
            required: true
            type: string
        -   name: dataSourceItemUid
            in: path
            description: dataSourceItemUid
            required: true
            type: string
        -   name: read_by_worker
            in: path
            description: read_by_worker
            required: false
            type: string
        -   name: done_by_worker
            in: body
            description: done_by_worker
            required: false
            type: string
        -   name: success
            in: body
            description: success
            required: false
            type: boolean
        -   name: fail_description
            in: body
            description: fail_description
            required: false
            type: string
        -   name: proxy_used
            in: body
            description: proxy_used
            required: false
            type: string            
        responses:
            200:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        description:
                            type: string
                            description: description
                        data:
                            type: object
                            description: data
        """
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
            job_schema = JobSchema()
            job_patch_schema = JobPatchSchema()
            clean_body, errors = job_patch_schema.load(body)
            if errors:
                logger.error("Errors in patch body: {}".format(errors))

            else:
                update_body = job_patch_schema.dump(clean_body)[0]
                update_body["modified"] = datetime.datetime.utcnow()
                q = Job.update(**update_body).where(Job.id == job_id)
                q.execute()
                updated_job = Job.select().where(Job.id == job_id).get()
                logger.info("Job {} updated".format(job_id))
                response = {"statusCode": 200,
                            "description": "Patch OK",
                            "data": job_schema.dump(updated_job)[0]}
                self.write(response)


class JobTableCleanUpHandler(DataRequestHandler):
    """Endpoint to delete recent jobs records"""
    SUPPORTED_METHODS = ["POST", "OPTIONS"]

    def options(self):
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_status(204)
        self.finish()

    def post(self):
        """Endpoint to delete recent jobs records
        ---
        description: Endpoint to delete recent jobs records
        responses:
            200:
                description: Success                
                schema:
                   type: object
                   properties:
                        statusCode:
                            type: integer
                            description: statusCode                       
                        description:
                            type: string
                            description: description                      
                        job:
                            type: string
                            description: job                         
        """
        now = datetime.datetime.utcnow()
        ago = now - datetime.timedelta(days=Config.JOB_CLEANUP_DAYS)  # how deep cleanup goes. Default to 7 days
        q = Job.delete().where(Job.created < ago)
        q.execute()
        logger.info("Jobs cleanup done")
        self.set_status(200)
        response = {"statusCode": 200, "job": None, "description": "Jobs cleaned up"}
        self.write(response)
