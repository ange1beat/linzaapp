namespace WebApi.Extensions.Environment;

public static class EnvironmentExtension
{
    private const string EnvName = "Local";

    public static bool IsLocal(this IHostEnvironment hostEnvironment)
    {
        return hostEnvironment.IsEnvironment(EnvName);
    }
}
