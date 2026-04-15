namespace Provider.Database.Auth.Recovery;

public interface IRecoverySettings
{
    TimeSpan OtpTokenTtl { get; }

    TimeSpan RecoveryTokenTtl { get; }
}
