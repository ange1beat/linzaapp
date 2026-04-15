using Domain.Cellular;

namespace Provider.Cellular;

public class SmsNadoClient : ICellularClient
{
    private const string Action = "post_sms";

    private readonly HttpClient _client;
    private readonly ISmsNadoClientSettings _settings;

    public SmsNadoClient(HttpClient client, ISmsNadoClientSettings settings)
    {
        _client = client;
        _settings = settings;
    }

    public async Task Send(SmsMessage message)
    {
        var parameters = new Dictionary<string, string>
        {
            { "action", Action },
            { "user", _settings.User },
            { "pass", _settings.Password },
            { "message", message.Body },
            { "target",  message.To},
            { "sender", _settings.Sender },
        };

        var content = new FormUrlEncodedContent(parameters);

        HttpResponseMessage response = await _client.PostAsync(string.Empty, content);

        response.EnsureSuccessStatusCode();
    }
}
