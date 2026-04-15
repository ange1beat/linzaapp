using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Context.Configs;

internal sealed class DbProjectMemberConfig : IEntityTypeConfiguration<DbProjectMember>
{
    public void Configure(EntityTypeBuilder<DbProjectMember> builder)
    {
        builder.ToTable("ProjectMembers");

        builder.HasKey(pu => new { pu.ProjectId, pu.UserId });

        builder.Property(pu => pu.CreatedBy).IsRequired();

        builder.Property(pu => pu.CreatedAt)
            .IsRequired()
            .HasDefaultValueSql("now()")
            .ValueGeneratedOnAdd();

        builder.HasIndex(pu => pu.ProjectId);
    }
}
