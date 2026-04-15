namespace WebApi.Models.Authentication.Guards;

public interface IResourceGuardSettings
{
    string SecretKey { get; }
}
