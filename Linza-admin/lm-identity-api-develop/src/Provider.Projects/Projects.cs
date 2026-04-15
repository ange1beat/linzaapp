using Domain.Projects;
using System.Net.Http.Json;

namespace Provider.Projects;

public class Projects : IProjects
{
    private readonly HttpClient _client;

    public Projects(HttpClient client)
    {
        _client = client;
    }

    public async Task<IReadOnlyCollection<string>> ProjectIds(string userId)
    {
        HttpResponseMessage response = await _client.GetAsync(
            $"v1/projects/membership/{userId}"
        );

        response.EnsureSuccessStatusCode();

        var membership = await response.Content.ReadFromJsonAsync<MembershipResponse>();

        if (membership is null)
        {
            throw new InvalidOperationException(
                $"Unexpected HTTP response from '{_client.BaseAddress}'"
            );
        }

        return membership.ProjectIds;
    }

    private record MembershipResponse(IReadOnlyCollection<string> ProjectIds);
}

