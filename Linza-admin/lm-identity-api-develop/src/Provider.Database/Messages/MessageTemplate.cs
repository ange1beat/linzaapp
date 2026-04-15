using Domain.Messages;

namespace Provider.Database.Messages;

internal class MessageTemplate : IMessageTemplate
{
    private readonly DbMessageTemplate _entity;

    public MessageTemplate(DbMessageTemplate entity)
    {
        _entity = entity;
    }

    public string Body(params MessageParam[] parameters)
    {
        return ParameterizedValue(_entity.Body, parameters);
    }

    public string Subject(params MessageParam[] parameters)
    {
        return ParameterizedValue(_entity.Subject, parameters);
    }

    private static string ParameterizedValue(string value, params MessageParam[] parameters)
    {
        return parameters.Aggregate(value, (res, param) =>
            res.Replace(param.Key, param.Value)
        );
    }
}
