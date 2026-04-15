namespace WebApi.Models.Requests.Auth;

public record OtpSmsRequest
{
    public string PhoneNumber { get; set; } = null!;
}
