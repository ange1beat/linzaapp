namespace Provider.Identity.Users;

internal class UserDto
{
    public string Id { get; set; } = null!;

    public List<UserRole> Roles { get; set; }  = null!;
}
