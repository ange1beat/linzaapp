using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Responses;

public class MembershipResponse
{
    [Required]
    public string UserId { get; set; }

    [Required]
    public IEnumerable<string> ProjectIds { get; set; }

    public MembershipResponse(string userId, IEnumerable<string> projectIds)
    {
        UserId = userId;
        ProjectIds = projectIds;
    }
}
