from marshmallow import Schema, fields, validate
from marshmallow.validate import Range


class ContentParsedSchema(Schema):
    author = fields.String(required=False, allow_none=True)
    content = fields.String(required=True)
    dataSourceItem = fields.Dict(allow_none=True)
    importedDateTime = fields.String(required=True, validate=validate.Regexp(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}..+)$"))
    publishedDateTime = fields.String(validate=validate.Regexp(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}..+)$"))
    title = fields.String(required=True)
    uid = fields.UUID(required=True)
    url = fields.String(required=True)
    contentType = fields.Integer(required=False, validate=validate.Range(min=0, max=20, error="Value out of range 0-20"))
    publishedDate = fields.String(required=False)
    publishedTime = fields.String(required=False)
    viewsCount = fields.Integer(missing=None, allow_none=True)
    aggregatedSocialReactionsCount = fields.Integer(allow_none=True)
    aggregatedRepostsCount = fields.Integer(allow_none=True)
    commentsCount = fields.Integer(allow_none=True)
    followersCount = fields.Integer(allow_none=True)


class GetParseResultMappingSchema(Schema):
    title = fields.Str(allow_none=True, default=None)
    content = fields.Str(allow_none=True, default=None)
    publishedDateTime = fields.Str(allow_none=True, default=None)
    author = fields.Str(allow_none=True, default=None)
    viewsCount = fields.Str(allow_none=True, default=None)
    commentsCount = fields.Str(allow_none=True, default=None)
    aggregatedSocialReactionsCount = fields.Str(allow_none=True, default=None)
    aggregatedRepostsCount = fields.Str(allow_none=True, default=None)
    followersCount = fields.Str(allow_none=True, default=None)
