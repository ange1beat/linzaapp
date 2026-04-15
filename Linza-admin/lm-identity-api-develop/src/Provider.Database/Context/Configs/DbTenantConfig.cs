using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Tenants;

namespace Provider.Database.Context.Configs;

internal sealed class DbTenantConfig : IEntityTypeConfiguration<DbTenant>
{
    public void Configure(EntityTypeBuilder<DbTenant> builder)
    {
        builder.ToTable("Tenants").HasKey(t => t.Id);

        builder.Property(t => t.Name).IsRequired();
    }
}
