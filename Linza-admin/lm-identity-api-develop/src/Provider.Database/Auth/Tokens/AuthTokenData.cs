using Domain.Auth.Factors;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Provider.Database.Auth.Tokens;

internal sealed class AuthTokenData
{
    [JsonProperty(ItemConverterType = typeof(StringEnumConverter))]
    public IList<FactorType> Factors { get; set; } = new List<FactorType>();

    [JsonProperty(ItemConverterType = typeof(StringEnumConverter))]
    public ISet<FactorType> FactorsVerified { get; set; } = new HashSet<FactorType>();

    public int FactorsRequiredNumber { get; set; }

    public bool IsCompleted()
    {
        return FactorsVerified.Intersect(Factors).Count() == FactorsRequiredNumber;
    }
}
