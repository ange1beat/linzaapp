from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin
from src.importer_api.schemas import HealthSchema, DataSourceSchema, DataSourceItemSchema

from . import schemas


spec = APISpec(
    title='Data Importing API',
    version='1.1',
    openapi_version='2.0',
    plugins=[
        TornadoPlugin(),
        MarshmallowPlugin(),
    ],
)

spec.components.definition('Health', schema=schemas.HealthSchema)

