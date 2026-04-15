using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests;

public class UpdateProjectMembers
{
    [Required]
    public IEnumerable<string> ProjectIds { get; set; } = null!;
}
