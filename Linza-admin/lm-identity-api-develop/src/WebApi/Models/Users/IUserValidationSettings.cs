namespace WebApi.Models.Users;

public interface IUserValidationSettings
{
    string NamePattern { get; }

    int AvatarMaxSizeKb { get; }
}
