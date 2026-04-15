using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Tenants;
using Provider.Database.Users;

namespace Provider.Database.Context.Configs;

internal sealed class DbUserConfig : IEntityTypeConfiguration<DbUser>
{
    public void Configure(EntityTypeBuilder<DbUser> builder)
    {
        builder.ToTable("Users").HasKey(u => u.Id);

        builder.Property(u => u.TenantId).IsRequired();
        builder.Property(u => u.FirstName).IsRequired();
        builder.Property(u => u.LastName).IsRequired();
        builder.Property(u => u.Email).IsRequired();
        builder.Property(u => u.PhoneNumber).IsRequired(false);
        builder.Property(u => u.TelegramUsername).IsRequired(false);
        builder.Property(u => u.PasswordHash).IsRequired();
        builder.Property(u => u.AccessFailedCount).IsRequired().HasDefaultValue(0);
        builder.Property(u => u.LockoutEndDate).IsRequired(false);
        builder.Property(u => u.LastFailedAccessDate).IsRequired(false);
        builder.Property(u => u.LastLoginDate).IsRequired(false);

        builder.Property(u => u.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.Property(u => u.UpdatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAddOrUpdate();

        builder.HasOne<DbTenant>()
            .WithMany()
            .HasForeignKey(u => u.TenantId)
            .OnDelete(DeleteBehavior.Restrict)
            .IsRequired();

        builder.HasOne(u => u.Avatar)
            .WithOne()
            .HasForeignKey<DbUserAvatar>(ua => ua.UserId)
            .OnDelete(DeleteBehavior.SetNull)
            .IsRequired(false);

        builder.HasMany(u => u.Roles)
            .WithOne()
            .HasForeignKey(r => r.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(u => u.Email).IsUnique();
        builder.HasIndex(u => u.PhoneNumber).IsUnique();
        builder.HasIndex(u => new { u.Email, u.PhoneNumber });
    }
}
