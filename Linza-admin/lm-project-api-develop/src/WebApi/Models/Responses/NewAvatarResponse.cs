namespace WebApi.Models.Responses;

public class NewAvatarResponse
{
    public string AvatarId { get; }

    public NewAvatarResponse(string avatarId)
    {
        AvatarId = avatarId;
    }
}
