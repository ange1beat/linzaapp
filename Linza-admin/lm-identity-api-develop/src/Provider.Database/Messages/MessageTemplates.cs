using Domain.Auth.Exceptions;
using Domain.Messages;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using System.Globalization;

namespace Provider.Database.Messages;

public class MessageTemplates : IMessageTemplates
{
    private readonly IdentityDbContext _dbCtx;

    public MessageTemplates(IdentityDbContext dbCtx)
    {
        _dbCtx = dbCtx;
    }

    public async Task<IMessageTemplate> Template(MessageType type, CultureInfo culture)
    {
        var templates = await _dbCtx.Set<DbMessageTemplate>()
            .Where(mt => mt.Type == type)
            .ToListAsync();

        if (templates.Count == 0)
        {
            throw new InvalidOperationException(
                $"Missing message template: type='{type.ToString()}'"
            );
        }

        var localizedTemplate = templates.FirstOrDefault(mt =>
            mt.Language == culture.Name || mt.Language == culture.Parent.Name
        );

        if (localizedTemplate is null)
        {
            throw new UnsupportedCultureException(culture);
        }

        return new MessageTemplate(localizedTemplate);
    }
}
