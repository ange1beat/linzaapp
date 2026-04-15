using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests;

public class AddProjectToFavoritesRequest
{
    [Required(AllowEmptyStrings = false)]
    public string ProjectId { get; set; } = null!;
}
