using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests;

public class UpdateFavoriteProjects
{
    [Required]
    [MinLength(1)]
    public IEnumerable<string> ProjectIds { get; set; } = null!;
}
