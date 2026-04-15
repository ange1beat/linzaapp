namespace Domain.Messages;

public interface IMessageTemplate
{
    string Body(params MessageParam[] parameters);

    string Subject(params MessageParam[] parameters);
}
