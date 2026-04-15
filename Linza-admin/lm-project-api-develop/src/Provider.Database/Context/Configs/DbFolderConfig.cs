using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Context.Configs;

internal sealed class DbFolderConfig : IEntityTypeConfiguration<DbFolder>
{
    public void Configure(EntityTypeBuilder<DbFolder> builder)
    {
        builder.ToTable("Folders");
        builder.HasKey(f => f.Id);

        builder.Property(f => f.Id).IsRequired();
        builder.Property(f => f.ProjectId).IsRequired();
        builder.Property(f => f.Name).IsRequired().IsUnicode();
        builder.Property(f => f.CreatedBy).IsRequired();
        builder.Property(f => f.UpdatedBy).IsRequired();

        builder.Property(f => f.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.Property(f => f.UpdatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAddOrUpdate();
    }
}
