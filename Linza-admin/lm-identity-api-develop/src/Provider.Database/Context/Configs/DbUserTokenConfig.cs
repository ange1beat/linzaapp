using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Tokens;

namespace Provider.Database.Context.Configs;

internal sealed class DbUserTokenConfig : IEntityTypeConfiguration<DbUserToken>
{
    public void Configure(EntityTypeBuilder<DbUserToken> builder)
    {
        builder.ToTable("UserTokens").HasKey(ut => ut.Id);

        builder.Property(ut => ut.Type).IsRequired().HasConversion<string>();
        builder.Property(ut => ut.Data).IsRequired(false);
        builder.Property(ut => ut.ExpiresAt).IsRequired();

        builder.Property(ut => ut.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.HasOne(ut => ut.User)
            .WithMany()
            .HasForeignKey(ut => ut.UserId)
            .IsRequired();

        builder.HasIndex(ut => new { ut.Id, ut.Type }).IsUnique(false);
    }
}
