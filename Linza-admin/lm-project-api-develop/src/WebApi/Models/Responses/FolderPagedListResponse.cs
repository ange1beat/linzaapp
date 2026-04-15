using Domain.Projects.Folders;

namespace WebApi.Models.Responses;

public class FolderPagedListResponse
{
    public IEnumerable<FolderResponse> Folders => _folders.Select(f =>
    {
        var response = new FolderResponse();
        f.Write(response);

        return response;
    });

    public int Total { get; set; }

    private readonly IEnumerable<IFolder> _folders;

    public FolderPagedListResponse(IEnumerable<IFolder> folders, int total)
    {
        _folders = folders;
        Total = total;
    }
}
