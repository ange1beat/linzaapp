using Domain.Media;
using Microsoft.IdentityModel.Tokens;

namespace Domain.Users;

// Not thread-safe
public class UserDetails : ReflectedMedia
{
    public string FirstName { get; private set; } = null!;
    public string LastName { get; private set; } = null!;
    public string Email { get; private set; } = null!;
    public string? PhoneNumber { get; private set; }
    public string? TelegramUsername { get; private set; }

    public UserDetails WithName(string firstName, string lastName)
    {
        if (firstName.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid first name", nameof(firstName));
        }

        if (lastName.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid last name", nameof(lastName));
        }

        FirstName = firstName;
        LastName = lastName;

        return this;
    }

    public UserDetails WithEmail(string email)
    {
        if (email.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid email", nameof(email));
        }

        Email = email;

        return this;
    }

    public UserDetails WithPhone(string phoneNumber)
    {
        if (phoneNumber.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid phone number", nameof(phoneNumber));
        }

        PhoneNumber = phoneNumber;

        return this;
    }

    public UserDetails WithTelegram(string username)
    {
        if (username.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid telegram username", nameof(username));
        }

        const char prefix = '@';
        TelegramUsername = username.StartsWith(prefix)
            ? username
            : $"{prefix}{username}";

        return this;
    }
}
