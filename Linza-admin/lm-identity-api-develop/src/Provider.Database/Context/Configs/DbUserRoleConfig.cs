using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Users;

namespace Provider.Database.Context.Configs;

internal sealed class DbUserRoleConfig : IEntityTypeConfiguration<DbUserRole>
{
    public void Configure(EntityTypeBuilder<DbUserRole> builder)
    {
        builder.ToTable("UserRoles").HasKey(ur => new { ur.UserId, ur.Role });

        builder.Property(ur => ur.Role).IsRequired().HasConversion<string>();
    }
}
