using System.Globalization;

namespace Domain.Messages;

public interface IMessageTemplates
{
    Task<IMessageTemplate> Template(MessageType type, CultureInfo culture);
}
