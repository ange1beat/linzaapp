using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Context.Configs;

internal sealed class DbProjectAvatarConfig : IEntityTypeConfiguration<DbProjectAvatar>
{
    public void Configure(EntityTypeBuilder<DbProjectAvatar> builder)
    {
        builder.ToTable("ProjectAvatars");
        builder.HasKey(pa => pa.Id);

        builder.Property(pa => pa.Id).IsRequired();
        builder.Property(pa => pa.FileName).IsRequired();
        builder.Property(pa => pa.ProjectId);
        builder.Property(pa => pa.CreatedBy).IsRequired();

        builder.Property(pa => pa.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();
    }
}
