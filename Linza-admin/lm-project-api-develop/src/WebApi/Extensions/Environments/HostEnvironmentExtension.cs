namespace WebApi.Extensions.Environments;

public static class HostEnvironmentExtension
{
    private const string LocalEnvName = "Local";

    public static bool IsLocal(this IHostEnvironment env)
    {
        return env.IsEnvironment(LocalEnvName);
    }
}
