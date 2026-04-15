using Domain.Messages;

namespace Provider.Database.Messages;

public class DbMessageTemplate
{
    public string Id { get; set; } = null!;

    public MessageType Type { get; set; }

    public string Language { get; set; } = null!;

    public string Subject { get; set; } = string.Empty;

    public string Body { get; set; } = null!;
}
