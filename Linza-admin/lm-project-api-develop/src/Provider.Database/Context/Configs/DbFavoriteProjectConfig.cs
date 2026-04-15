using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Context.Configs;

internal class DbFavoriteProjectConfig : IEntityTypeConfiguration<DbFavoriteProject>
{
    public void Configure(EntityTypeBuilder<DbFavoriteProject> builder)
    {
        builder.ToTable("FavoriteProjects");
        builder.HasKey(fp => new { fp.ProjectId, fp.UserId });

        builder.Property(pf => pf.TenantId).IsRequired();
        builder.Property(pf => pf.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.HasIndex(fp => new { fp.UserId, fp.TenantId });
    }
}
