namespace Domain.Guid;

public class ShortGuid
{
    private const int BaseLength = 22;

    private readonly System.Guid _guid;

    public ShortGuid(System.Guid guid)
    {
        _guid = guid;
    }

    public override string ToString()
    {
        return Convert.ToBase64String(_guid.ToByteArray())[..BaseLength]
            .Replace("/", "fs")
            .Replace("+", "up");
    }
}
