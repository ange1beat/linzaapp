namespace Provider.Database.Users;

public interface IUserSettings
{
    string AvatarScope { get; }

    TimeSpan OtpTokenTtl { get; }

    TimeSpan EmailInterval { get; }

    TimeSpan SmsInterval { get; }
}
