using Domain.Auth.Tokens;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace Provider.Database.Auth.Tokens;

internal sealed class VerificationTokenData
{
    [JsonConverter(typeof(StringEnumConverter))]
    public required VerificationScope Scope { get; init; }

    public required string Code { get; init; }

    public IDictionary<string, string> Properties { get; init; } =
        new Dictionary<string, string>();
}
