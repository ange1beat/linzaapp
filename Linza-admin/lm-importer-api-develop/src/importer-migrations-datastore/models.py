from playhouse import postgres_ext as pg
import uuid
import datetime
from config import Config


datastore = pg.PostgresqlExtDatabase(
    Config.IMPORTER_DATASTORE_DBNAME,
    user=Config.IMPORTER_DATASTORE_DBUSER,
    password=Config.IMPORTER_DATASTORE_DBPASS,
    host=Config.IMPORTER_DATASTORE_HOST,
    port=Config.IMPORTER_DATASTORE_PORT,
    autocommit=True, autorollback=True
)


class BaseModel(pg.Model):
    id = pg.UUIDField(primary_key=True, default=uuid.uuid4(), null=False)
    created = pg.DateTimeField(default=datetime.datetime.utcnow)
    modified = pg.DateTimeField(null=True)

    class Meta:
        database = datastore


class Health(BaseModel):
    name = pg.CharField()
    status = pg.CharField()


class DataSourceItem(BaseModel):    
    title = pg.CharField(max_length=10000, null=True)
    description = pg.TextField()
    iconUri = pg.CharField(max_length=10000)
    url = pg.CharField(max_length=10000)
    type = pg.CharField()
    updateInterval = pg.IntegerField(default=3600)
    config = pg.JSONField()
    account = pg.JSONField()
    isAutoCreated = pg.BooleanField(default=True)
    isActive = pg.BooleanField(default=False)
    timezone = pg.CharField(default="UTC")
    updated = pg.DateTimeField(default=datetime.datetime.utcnow)


class Job(BaseModel):

    dataSourceItemUid = pg.UUIDField()
    # read_by_scheduler = pg.DateTimeField()
    # posted_by_scheduler = pg.DateTimeField()
    read_by_worker = pg.DateTimeField(null=True)
    done_by_worker = pg.DateTimeField(null=True)
    success = pg.BooleanField(default=True)
    fail_description = pg.TextField(null=True)
    proxy_used = pg.CharField(null=True)


class StatsHistory(BaseModel):
    dataSourceItem = pg.ForeignKeyField(DataSourceItem)
    lastUpdated = pg.DateTimeField()
    audience = pg.IntegerField(null=True)


def create_tables_datastore():
    Health.create_table(True)    
    DataSourceItem.create_table(True)
    Job.create_table(True)