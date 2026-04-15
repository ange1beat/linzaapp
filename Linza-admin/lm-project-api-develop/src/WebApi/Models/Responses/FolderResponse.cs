using Domain.Media;

namespace WebApi.Models.Responses;

public class FolderResponse : ReflectedMedia
{
    public string Id { get; set; } = null!;

    public string Name { get; set; } = null!;
}
