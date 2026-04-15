namespace Domain.Auth.Tokens;

public record AuthToken(
    string AccessToken,
    string RefreshToken,
    DateTime AccessExpiresAt,
    DateTime RefreshExpiresAt
);
