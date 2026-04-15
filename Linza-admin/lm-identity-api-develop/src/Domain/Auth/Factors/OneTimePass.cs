using System.Text;

namespace Domain.Auth.Factors;

public class OneTimePass : IOneTimePass
{
    public string NextValue()
    {
        StringBuilder sb = new StringBuilder();
        List<int> intRange = Enumerable.Range(0, 9).Select(x => x).ToList();

        for (int i = 0; i < 6; i++)
        {
            sb.Append(intRange[Random.Shared.Next(0, intRange.Count - 1)]);
        }

        return sb.ToString();
    }
}
