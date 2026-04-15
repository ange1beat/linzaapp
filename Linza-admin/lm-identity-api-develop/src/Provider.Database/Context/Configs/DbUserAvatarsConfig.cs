using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Users;

namespace Provider.Database.Context.Configs;

internal sealed class UserAvatarsDbConfig : IEntityTypeConfiguration<DbUserAvatar>
{
    public void Configure(EntityTypeBuilder<DbUserAvatar> builder)
    {
        builder.ToTable("UserAvatars").HasKey(a => a.Id);

        builder.Property(a => a.Id).IsRequired();
        builder.Property(a => a.FileName).IsRequired();
        builder.Property(a => a.UserId);
        builder.Property(a => a.CreatedBy).IsRequired();

        builder.Property(a => a.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();
    }
}
