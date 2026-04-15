using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Tenants;
using Provider.Database.Users.Invitations;

namespace Provider.Database.Context.Configs;

internal sealed class DbInvitationConfig : IEntityTypeConfiguration<DbInvitation>
{
    public void Configure(EntityTypeBuilder<DbInvitation> builder)
    {
        builder.ToTable("Invitations").HasKey(inv => inv.Id);

        builder.Property(inv => inv.UserEmail).IsRequired();
        builder.Property(inv => inv.TenantId).IsRequired();
        builder.Property(inv => inv.UserRole).IsRequired().HasConversion<string>();
        builder.Property(inv => inv.CreatedBy).IsRequired();
        builder.Property(inv => inv.ExpiresAt).IsRequired();

        builder.Property(u => u.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.HasOne<DbTenant>()
            .WithMany()
            .HasForeignKey(inv => inv.TenantId)
            .OnDelete(DeleteBehavior.Cascade)
            .IsRequired();

        builder.HasIndex(inv => inv.UserEmail).IsUnique();
    }
}
