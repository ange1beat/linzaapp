import sys
from os.path import dirname, abspath
# Hack to import shared modules from parent directory
sys.path.append(dirname(dirname(abspath(__file__))))
from marshmallow import Schema, fields, validate, pre_load
from marshmallow.validate import Range
from config import Config
from tornado_swagger.model import register_swagger_model


class BaseSchema(Schema):
    id = fields.UUID(dump_to="uid", load_from="uid", required=True)
    created = fields.DateTime()
    modified = fields.DateTime(allow_none=True)

    class Meta:
        ordered = True


class HealthSchema(Schema):
    status = fields.String()
    name = fields.String()


class ConfigItem(Schema):
    query = fields.Str(required=True)
    method = fields.Str(required=True,
                        validate=validate.OneOf(["xpath"], error="Not a valid field value. 'xpath' is allowed now"))


class AreaExcludeSchema(Schema):
    area = fields.Nested(ConfigItem, many=True, required=True)
    exclude = fields.Nested(ConfigItem, many=True, allow_none=True)


class MonitoringAreaSchema(Schema):
    area = fields.Nested(ConfigItem, many=True, required=True)
    exclude = fields.Nested(ConfigItem, many=True, required=True)
    links_filter = fields.List(fields.Str(), required=True)


class MappingSchema(Schema):
    title = fields.Nested(AreaExcludeSchema)
    content = fields.Nested(AreaExcludeSchema, required=True)
    publishedDateTime = fields.Nested(AreaExcludeSchema, allow_none=True)
    author = fields.Nested(AreaExcludeSchema, allow_none=True)
    viewsCount = fields.Nested(AreaExcludeSchema, allow_none=True)
    commentsCount = fields.Nested(AreaExcludeSchema, allow_none=True)


class DataSourceItemConfigSchema(Schema):
    monitoring_area = fields.Nested(MonitoringAreaSchema, allow_none=True)
    # links = fields.Nested(ConfigItem, allow_none=True)
    mapping = fields.Nested(MappingSchema, allow_none=True)


# class RSSDataSourceItemConfigSchema(Schema):
#     links = fields.Nested(ConfigItem, allow_none=True)
#     mapping = fields.Nested(MappingSchema)

@register_swagger_model
class DataSourceSchema(BaseSchema):

    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=100000))
    updateInterval = fields.Integer(required=True, validate=Range(min=1, error="Value must be greater than 0"))
    isActive = fields.Boolean(required=True, default=False)
    isQuasy = fields.Boolean(required=True, default=False)
    iconUri = fields.String(required=True)
    timezone = fields.String(missing='UTC')


class DataSourceItemSchema(BaseSchema):

    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=10000))
    iconUri = fields.String(required=True, validate=validate.Length(max=10000))
    type = fields.String(required=True, validate=validate.OneOf(choices=Config.TYPES))
    url = fields.Str(required=True, validate=validate.Regexp(r"(.+:\/\/?.+)"))
    updateInterval = fields.Integer(validate=Range(min=300, error="Value must be 300 seconds or greater"))    
    isActive = fields.Boolean(required=True, default=False)
    isAutoCreated = fields.Boolean(default=True)
    config = fields.Nested(DataSourceItemConfigSchema, missing={})
    account = fields.Dict(missing={})
    timezone = fields.String(missing="UTC")
    updated = fields.DateTime(allow_none=True)

class DataSourceItemSearchSchema(BaseSchema):

    id = fields.String(required=True, validate=validate.Length(max=100))
    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=10000))
    iconUri = fields.String(required=True, validate=validate.Length(max=10000))
    type = fields.String(required=True, validate=validate.OneOf(choices=Config.TYPES))
    url = fields.Str(required=True, validate=validate.Regexp(r"(.+:\/\/?.+)"))
    updateInterval = fields.Integer(validate=Range(min=300, error="Value must be 300 seconds or greater"))    
    isActive = fields.Boolean(required=True, default=False)
    isAutoCreated = fields.Boolean(default=True)
    config = fields.Nested(DataSourceItemConfigSchema, missing={})
    account = fields.Dict(missing={})
    timezone = fields.String(missing="UTC")
    updated = fields.DateTime(allow_none=True)
    executionStatus = fields.String()
    lastResult = fields.String()
    nextLaunch = fields.Integer()

class DataSourcesItemsByUidsSchema(BaseSchema):

    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=10000))
    iconUri = fields.String(required=True, validate=validate.Length(max=10000))
    type = fields.String(required=True, validate=validate.OneOf(choices=Config.TYPES))
    url = fields.Str(required=True, validate=validate.Regexp(r"(.+:\/\/?.+)"))
    updateInterval = fields.Integer(validate=Range(min=300, error="Value must be greater than 300"))
    dataSource = fields.Nested(DataSourceSchema)
    isActive = fields.Boolean(required=True, default=False)
    isAutoCreated = fields.Boolean(default=True)
    config = fields.Nested(DataSourceItemConfigSchema, missing={})
    account = fields.Dict(missing={})
    timezone = fields.String(missing="UTC")
    updated = fields.DateTime(allow_none=True)


class DataSourcePostSchema(Schema):

    dataSource = fields.Nested(DataSourceSchema, required=True)
    dataSourceItems = fields.Nested(DataSourceItemSchema, many=True)


class DataSourcePutSchema(Schema):

    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=100000))
    updateInterval = fields.Integer(required=True,
                                    validate=Range(min=1, error="Value must be greater than 0"))
    isActive = fields.Boolean(required=True)
    isQuasy = fields.Boolean(required=True)
    iconUri = fields.String(required=True)
    timezone = fields.String(missing='UTC')


class DataSourcePatchSchema(Schema):

    title = fields.String(required=False, validate=validate.Length(max=10000))
    description = fields.String(required=False, validate=validate.Length(max=100000))
    updateInterval = fields.Integer(required=False,
                                    validate=Range(min=1, error="Value must be greater than 0"))
    isActive = fields.Boolean(required=False)
    isQuasy = fields.Boolean(required=False)
    iconUri = fields.String(required=False)
    timezone = fields.String()


class SetupSchema(Schema):
    url = fields.URL(required=True)
    type = fields.String(required=True)
    config = fields.Dict()
    parsing = fields.Dict()


class SocialNetworkCSVSchema(Schema):

    Url = fields.String(required=True, validate=validate.Regexp(r"(https?:\/\/)vk.com\/wall(.+)"))
    Content = fields.String(required=True, allow_none=False)
    Type = fields.String()
    Author = fields.String(required=True, allow_none=True)
    AuthorLink = fields.String(allow_none=True, validate=validate.Regexp(r"$|http(.+)"))
    Date = fields.String(required=True, validate=validate.Regexp(r"(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]) (0[0-9]|1[0-9]|2[0-9]|3[0-1]).(0[0-9]|1[0-2]).([0-9][0-9][0-9][0-9])$"))
    AggregatedSocialReactionsCount = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    CommentsCount = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    AggregatedRepostsCount = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    Clicks = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    WikiViews = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    ViewsCount = fields.Integer(required=False, default=None, missing=None, allow_none=True)
    timezone = fields.String(default="UTC")

    @pre_load
    def default_if_null(self, item):
        if not item["AggregatedSocialReactionsCount"]:
            item["AggregatedSocialReactionsCount"] = None
        if not item["CommentsCount"]:
            item["CommentsCount"] = None
        if not item["AggregatedRepostsCount"]:
            item["AggregatedRepostsCount"] = None
        if not item["CommentsCount"]:
            item["CommentsCount"] = None
        if not item["Clicks"]:
            item["Clicks"] = None
        if not item["WikiViews"]:
            item["WikiViews"] = None
        if not item["ViewsCount"]:
            item["ViewsCount"] = None
        if not item["AuthorLink"]:
            item["AuthorLink"] = None
        return item

    class Meta:
        exclude = tuple("timezone")


class IntegrumSchema(Schema):

    Source = fields.String(required=True, allow_none=False)
    Date = fields.String(required=True, validate=validate.Regexp(r"(0[0-9]|1[0-9]|2[0-9]|3[0-1]).(0[0-9]|1[0-2]).([0-9][0-9])$"))
    Time = fields.String(required=True, validate=validate.Regexp(r"(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"))
    Title = fields.String(required=True, validate=validate.Length(max=10000))
    Content = fields.String(required=True, allow_none=False)
    Uri = fields.String(required=True, validate=validate.Regexp(r"(https?:\/\/)(.+)"), allow_none=False)
    Author = fields.String(required=False, allow_none=True)
    timezone = fields.String(missing="UTC")

    class Meta:
        exclude = tuple("timezone")


class SocialIntegrumSchema(Schema):

    bloger = fields.String(required=True, max=10000)
    dateTime = fields.String(required=True, validate=validate.Regexp(
        r"(0[0-9]|1[0-9]|2[0-9]|3[0-1]).(0[0-9]|1[0-2]).([0-9][0-9]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$"))
    headerText = fields.String(required=True, allow_none=False)
    platform = fields.String(required=True, validate=validate.Regexp(r"(https?:\/\/)(.+)"), allow_none=False)
    audience = fields.Integer(required=True, allow_none=True)
    timezone = fields.String(missing="UTC")

    @pre_load
    def default_if_null(self, item):
        if not item["audience"]:
            item["audience"] = None

    class Meta:
        exclude = tuple("timezone")


class JobSchema(BaseSchema):

    dataSourceItemUid = fields.UUID(required=True)
    # posted_by_scheduler = fields.DateTime(allow_none=True)
    read_by_worker = fields.DateTime(allow_none=True)
    done_by_worker = fields.DateTime(allow_none=True)
    success = fields.Boolean(default=True)
    fail_description = fields.String(allow_none=True)
    proxy_used = fields.String(allow_none=True)


class JobPatchSchema(Schema):

    dataSourceItemUid = fields.UUID(required=False)
    # posted_by_scheduler = fields.DateTime(allow_none=True)
    read_by_worker = fields.DateTime(required=False)
    done_by_worker = fields.DateTime(required=False)
    success = fields.Boolean(required=False)
    fail_description = fields.String(required=False)
    proxy_used = fields.String(allow_none=True)


class ScreenshotSchema(BaseSchema):

    dataSourceItemUid = fields.UUID(required=True)
    url = fields.String(required=True)
    isRead = fields.Bool(default=False, allow_none=True)


class ScreenshotPatchSchema(Schema):

    dataSourceItem = fields.Dict(allow_nonw=True)
    url = fields.String(allow_none=True)
    isRead = fields.Bool(allow_none=True)


class DataSourceItemPutSchema(Schema):

    title = fields.String(required=True, validate=validate.Length(max=10000))
    description = fields.String(required=True, validate=validate.Length(max=10000))
    iconUri = fields.String(required=True, validate=validate.Length(max=10000))
    type = fields.String(required=True, validate=validate.OneOf(choices=Config.TYPES))
    url = fields.Str(required=True, validate=validate.Regexp(r"(.+:\/\/?.+)"))
    updateInterval = fields.Integer(validate=Range(min=1, error="Value must be greater than 0"))    
    isActive = fields.Boolean(required=True)
    isAutoCreated = fields.Boolean()
    config = fields.Nested(DataSourceItemConfigSchema)
    account = fields.Dict()
    timezone = fields.String()
    updated = fields.DateTime()


class DataSourceItemPatchSchema(Schema):

    title = fields.String(required=False, validate=validate.Length(max=10000))
    description = fields.String(required=False, validate=validate.Length(max=10000))
    iconUri = fields.String(required=False, validate=validate.Length(max=10000))
    type = fields.String(required=False, validate=validate.OneOf(choices=Config.TYPES))
    url = fields.Str(required=False, validate=validate.Regexp(r"(.+:\/\/?.+)"))
    updateInterval = fields.Integer(required=False, validate=Range(min=1, error="Value must be greater than 0"))    
    isActive = fields.Boolean(required=False, default=False)
    isAutoCreated = fields.Boolean(required=False)
    config = fields.Nested(DataSourceItemConfigSchema)
    account = fields.Dict()
    timezone = fields.String()


class GetWEBLinksMonitoringAreaItemsSchema(Schema):
    query = fields.Str(required=True)
    method = fields.Str(required=True)


class GetWEBLinksMonitoringAreaSchema(Schema):
    area = fields.Nested(GetWEBLinksMonitoringAreaItemsSchema, many=True, required=True)
    exclude = fields.Nested(GetWEBLinksMonitoringAreaItemsSchema, many=True)
    links_filter = fields.List(fields.Str(), required=True)


class GetWEBLinksSchema(Schema):
    url = fields.Url(required=True)
    monitoring_area = fields.Nested(GetWEBLinksMonitoringAreaSchema, required=True)


class GetParseResultMappingSchema(Schema):
    title = fields.Nested(AreaExcludeSchema, allow_none=True)
    content = fields.Nested(AreaExcludeSchema, allow_none=True)
    publishedDateTime = fields.Nested(AreaExcludeSchema, allow_none=True)
    author = fields.Nested(AreaExcludeSchema, allow_none=True)
    viewsCount = fields.Nested(AreaExcludeSchema, allow_none=True)
    commentsCount = fields.Nested(AreaExcludeSchema, allow_none=True)


class GetParseResultSchema(Schema):
    url = fields.Url(required=True)
    mapping = fields.Nested(GetParseResultMappingSchema, required=True)


class TelegramSchema(BaseSchema):
    phone = fields.Str(required=True)
    code = fields.Int(allow_none=True)
    auth_request = fields.Int(allow_none=True)
    datetime = fields.DateTime(allow_none=True)
