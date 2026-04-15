using Domain.Authentication;
using Domain.Exceptions;
using Domain.Users;
using Domain.Users.Exceptions;
using Domain.Users.Rules;
using Newtonsoft.Json;
using System.Net;
using System.Net.Http.Headers;

namespace Provider.Identity.Users;

public class Users : IUsers
{
    private readonly HttpClient _client;

    public Users(HttpClient client)
    {
        _client = client;
    }

    public async Task<IUser> User(string userId, IUserIdentity requester)
    {
        new UserCanRequestUsersRule(requester).Enforce();
        var httpRequest = new HttpRequestMessage(HttpMethod.Get, $"v1/users/{userId}");

        httpRequest.Headers.Authorization = new AuthenticationHeaderValue(
            "Bearer",
            requester.AccessToken()
        );

        HttpResponseMessage httpResponse;
        try
        {
            httpResponse = await _client.SendAsync(httpRequest);
            httpResponse.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException exc)
        {
            Exception error = exc.StatusCode switch
            {
                HttpStatusCode.Unauthorized => new UnauthorizedAccessException(),
                HttpStatusCode.Forbidden    => new AccessDeniedException(requester, exc.Message),
                HttpStatusCode.NotFound     => new UserNotFoundException(userId),

                _ => exc
            };

            throw error;
        }

        var userDto = JsonConvert.DeserializeObject<UserDto>(
            await httpResponse.Content.ReadAsStringAsync()
        );

        if (userDto is null)
        {
            throw new InvalidOperationException(
                $"Unexpected HTTP response from '{httpRequest.RequestUri}'"
            );
        }

        return new User(userDto, requester);
    }

    public async Task<IReadOnlyCollection<IUser>> AllUsers(
        IEnumerable<string> userIds,
        IUserIdentity requester)
    {
        new UserCanRequestUsersRule(requester).Enforce();

        userIds = userIds.ToHashSet();
        if (!userIds.Any())
        {
            return new List<IUser>();
        }

        IEnumerable<UserDto> tenantUsers = await TenantUsers(requester);

        var unknownUsers = userIds.Except(tenantUsers.Select(tu => tu.Id)).ToList();
        if (unknownUsers.Count != 0)
        {
            throw new UsersNotFoundException(unknownUsers);
        }

        return tenantUsers
            .Where(u => userIds.Contains(u.Id))
            .Select(u => new User(u, requester))
            .ToList();
    }

    public async Task<IReadOnlyCollection<IUser>> Supervisors(IUserIdentity requester)
    {
        new UserCanRequestUsersRule(requester).Enforce();

        IEnumerable<UserDto> usersDto = await TenantUsers(requester);

        return usersDto
            .Where(u => u.Roles.Contains(UserRole.Supervisor))
            .Select(u => new User(u, requester))
            .ToList();
    }

    private class TenantUsersDto
    {
        public IReadOnlyCollection<UserDto> Users { get; set; } = null!;
    }

    private async Task<IReadOnlyCollection<UserDto>> TenantUsers(IUserIdentity requester)
    {
        var httpRequest = new HttpRequestMessage(
            HttpMethod.Get,
            $"v1/tenants/{requester.TenantId}/users"
        );

        httpRequest.Headers.Authorization = new AuthenticationHeaderValue(
            "Bearer",
            requester.AccessToken()
        );

        var httpResponse = await _client.SendAsync(httpRequest);
        httpResponse.EnsureSuccessStatusCode();

        var tenantUsers = JsonConvert.DeserializeObject<TenantUsersDto>(
            await httpResponse.Content.ReadAsStringAsync()
        );

        return tenantUsers?.Users ?? throw new InvalidOperationException(
            $"Unexpected HTTP response from '{httpRequest.RequestUri}'"
        );
    }
}
