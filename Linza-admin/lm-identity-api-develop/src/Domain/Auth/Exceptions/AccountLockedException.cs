namespace Domain.Auth.Exceptions;

public class AccountLockedException : Exception
{
    public DateTime LockoutEndDate { get; }

    public AccountLockedException(DateTime lockoutEndDate) : base("Account is locked")
    {
        LockoutEndDate = lockoutEndDate;
    }
}
