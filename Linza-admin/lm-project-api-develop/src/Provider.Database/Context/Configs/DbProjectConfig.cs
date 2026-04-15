using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Context.Configs;

internal sealed class DbProjectConfig : IEntityTypeConfiguration<DbProject>
{
    public void Configure(EntityTypeBuilder<DbProject> builder)
    {
        builder.ToTable("Projects");
        builder.HasKey(x => x.Id);

        builder.Property(p => p.Id).IsRequired();
        builder.Property(p => p.TenantId).IsRequired();
        builder.Property(p => p.Name).IsRequired().IsUnicode();
        builder.Property(p => p.CreatedBy).IsRequired();
        builder.Property(p => p.UpdatedBy).IsRequired();
        builder.Property(p => p.RowVersion).IsRowVersion();

        builder.Property(p => p.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.Property(p => p.UpdatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAddOrUpdate();

        builder.HasMany<DbProjectMember>(p => p.Members)
            .WithOne(pm => pm.Project)
            .HasForeignKey(pu => pu.ProjectId)
            .OnDelete(DeleteBehavior.Cascade)
            .IsRequired();

        builder.HasOne<DbProjectAvatar>(p => p.Avatar)
            .WithOne()
            .HasForeignKey<DbProjectAvatar>(pa => pa.ProjectId)
            .OnDelete(DeleteBehavior.SetNull)
            .IsRequired(false);

        builder.HasMany<DbFolder>()
            .WithOne()
            .HasForeignKey(pf => pf.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(p => p.TenantId);
    }
}
