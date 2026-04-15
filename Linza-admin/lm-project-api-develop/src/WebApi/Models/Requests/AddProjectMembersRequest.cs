using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests;

public class AddProjectMembersRequest
{
    [Required]
    public IEnumerable<string> UserIds { get; set; } = null!;
}
