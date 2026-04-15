using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Messages;

namespace Provider.Database.Context.Configs;

public class DbMessageTemplateConfig : IEntityTypeConfiguration<DbMessageTemplate>
{
    public void Configure(EntityTypeBuilder<DbMessageTemplate> builder)
    {
        builder.ToTable("MessageTemplates").HasKey(mt => mt.Id);

        builder.Property(mt => mt.Type).IsRequired().HasConversion<string>();
        builder.Property(mt => mt.Language).IsRequired();
        builder.Property(mt => mt.Subject).IsRequired().HasDefaultValue("");
        builder.Property(mt => mt.Body).IsRequired();
    }
}
