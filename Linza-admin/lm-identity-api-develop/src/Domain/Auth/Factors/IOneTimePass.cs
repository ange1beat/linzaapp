namespace Domain.Auth.Factors;

public interface IOneTimePass
{
    public string NextValue();
}
