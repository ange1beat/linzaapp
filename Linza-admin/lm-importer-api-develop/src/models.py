#models for API
from playhouse import postgres_ext as pg
import logging
import uuid
import json
import pytz
from datetime import datetime
from config import Config
import os
import time


def get_settings():
    with open('conf.json') as f:
        settings = json.load(f)
        return settings


# settings = get_settings()

datastore = pg.PostgresqlExtDatabase(
    Config.IMPORTER_DATASTORE_DBNAME,
    user=Config.IMPORTER_DATASTORE_DBUSER,
    password=Config.IMPORTER_DATASTORE_DBPASS,
    host=Config.IMPORTER_DATASTORE_HOST,
    port=Config.IMPORTER_DATASTORE_PORT,
    autocommit=True, autorollback=True
)

filestore = pg.PostgresqlExtDatabase(
    Config.IMPORTER_FILESTORE_DBNAME,
    user=Config.IMPORTER_FILESTORE_DBUSER,
    password=Config.IMPORTER_FILESTORE_DBPASS,
    host=Config.IMPORTER_FILESTORE_HOST,
    port=Config.IMPORTER_FILESTORE_PORT,
    autocommit=True, autorollback=True
)


class FilesBaseModel(pg.Model):
    id = pg.UUIDField(primary_key=True, null=False)
    created = pg.DateTimeField(default=datetime.utcnow)
    modified = pg.DateTimeField(default=datetime.utcnow)

    class Meta:
        database = filestore


class BaseModel(pg.Model):
    id = pg.UUIDField(primary_key=True, null=False)
    created = pg.DateTimeField(default=datetime.utcnow)
    modified = pg.DateTimeField(default=datetime.utcnow)

    class Meta:
        database = datastore


class Health(BaseModel):
    name = pg.CharField()
    status = pg.CharField()


class Telegram(BaseModel):
    phone = pg.CharField(max_length=14, unique=True, null=True)
    code = pg.IntegerField(default=0)
    auth_request = pg.BooleanField(default=False)
    datetime = pg.DateTimeField(default=datetime.now())


class DataSource(BaseModel):
    title = pg.CharField(max_length=10000, null=True)
    description = pg.TextField()
    iconUri = pg.CharField(max_length=10000)
    isQuasy = pg.BooleanField(default=False)
    updateInterval = pg.IntegerField(default=3600)
    isActive = pg.BooleanField(default=False)
    timezone = pg.CharField(default="UTC")


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
    updated = pg.DateTimeField(default=datetime.utcnow)


class SocialNetworkCSV(FilesBaseModel):

    Url = pg.CharField(max_length=10000)
    Content = pg.TextField()
    Type = pg.CharField()
    Author = pg.CharField(max_length=10000)
    AuthorLink = pg.CharField(max_length=10000)
    Date = pg.DateTimeField()
    AggregatedSocialReactionsCount = pg.IntegerField(null=True)
    CommentsCount = pg.IntegerField(null=True)
    AggregatedRepostsCount = pg.IntegerField(null=True)
    Clicks = pg.IntegerField(null=True)
    WikiViews = pg.IntegerField(null=True)
    ViewsCount = pg.IntegerField(null=True)
    is_read = pg.BooleanField(default=False)
    filename = pg.CharField()
    timezone = pg.CharField(default="UTC")


class Integrum(FilesBaseModel):

    Source = pg.CharField(max_length=10000)
    Date = pg.CharField()
    Time = pg.CharField()
    DateTime = pg.DateTimeField()
    Title = pg.CharField(max_length=10000)
    Content = pg.TextField()
    Uri = pg.CharField(max_length=10000)
    Author = pg.CharField(max_length=10000, null=True)
    is_read = pg.BooleanField()
    filename = pg.CharField()
    timezone = pg.CharField(default="UTC")


class SocialIntegrum(FilesBaseModel):

    bloger = pg.CharField(max_length=10000)
    dateTime = pg.DateTimeField()
    headerText = pg.TextField()
    platform = pg.CharField(max_length=10000)
    audience = pg.IntegerField(null=True)
    is_read = pg.BooleanField(default=False)
    filename = pg.CharField()
    timezone = pg.CharField(default="UTC")


class Job(BaseModel):

    dataSourceItemUid = pg.UUIDField()
    # read_by_scheduler = pg.DateTimeField()
    # posted_by_scheduler = pg.DateTimeField()
    read_by_worker = pg.DateTimeField(null=True)
    done_by_worker = pg.DateTimeField(null=True)
    success = pg.BooleanField(default=True)
    fail_description = pg.TextField(null=True)
    proxy_used = pg.CharField(null=True)


class Screenshot(BaseModel):

    dataSourceItemUid = pg.UUIDField(null=False)
    url = pg.CharField(null=False)
    isRead = pg.BooleanField(default=False)


class StatsHistory(BaseModel):
    dataSourceItem = pg.ForeignKeyField(DataSourceItem)
    lastUpdated = pg.DateTimeField()
    audience = pg.IntegerField(null=True)


class Import(FilesBaseModel):

    rows_total = pg.IntegerField()
    rows_success = pg.IntegerField()
    filename = pg.CharField(max_length=255)
    fail_description = pg.TextField()
    user = pg.UUIDField()


def create_tables_datastore():
    Health.create_table(True)
    Telegram.create_table(True)
    DataSource.create_table(True)
    DataSourceItem.create_table(True)
    Job.create_table(True)


def create_tables_filestore():
    Import.create_table(True)
    SocialNetworkCSV.create_table(True)
    Integrum.create_table(True)
    SocialIntegrum.create_table(True)
