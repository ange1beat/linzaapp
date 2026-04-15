using System.ComponentModel.DataAnnotations;
using WebApi.Attributes;

namespace WebApi.Models.Requests;

public class UpdateProjectNameRequest
{
    [Required]
    [ProjectName]
    public string Name { get; set; } = null!;
}
