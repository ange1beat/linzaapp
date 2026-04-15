using System.Globalization;

namespace WebApi.Models.Files;

public class JenkinsHash
{
    private readonly byte[] _bytes;

    public JenkinsHash(byte[] bytes)
    {
        _bytes = bytes;
    }

    public override string ToString()
    {
        uint hash = 0;

        foreach (var c in _bytes)
        {
            hash += c;
            hash += (hash << 10);
            hash ^= (hash >> 6);
        }

        hash += (hash << 3);
        hash ^= (hash >> 11);
        hash += (hash << 15);

        return hash.ToString("X", CultureInfo.InvariantCulture);
    }
}
