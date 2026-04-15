namespace WebApi.Models.Responses.Auth;

public class OtpChallengeResponse
{
    public string OtpId { get; }

    public OtpChallengeResponse(string otpId)
    {
        OtpId = otpId;
    }
}
