namespace Domain.Rules;

public interface IRule
{
    bool Match();

    void Enforce();
}
