using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Provider.Database.Migrations;

/// <inheritdoc />
public partial class UpdateInvitations_AddColumnAndIndex : Migration
{
    /// <inheritdoc />
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.RenameColumn(
            name: "Role",
            table: "Invitations",
            newName: "UserRole");

        migrationBuilder.AddColumn<DateTime>(
            name: "ExpiresAt",
            table: "Invitations",
            type: "timestamp with time zone",
            nullable: false,
            defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

        migrationBuilder.CreateIndex(
            name: "IX_Invitations_UserEmail",
            table: "Invitations",
            column: "UserEmail",
            unique: true);
    }

    /// <inheritdoc />
    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropIndex(
            name: "IX_Invitations_UserEmail",
            table: "Invitations");

        migrationBuilder.DropColumn(
            name: "ExpiresAt",
            table: "Invitations");

        migrationBuilder.RenameColumn(
            name: "UserRole",
            table: "Invitations",
            newName: "Role");
    }
}
