using System.ComponentModel.DataAnnotations;
using Domain.Projects;
using Domain.Projects.Folders;

namespace WebApi.Models.Requests;

public class RenameFolderRequest
{
    [Required]
    // ToDo: add folder name validation
    [MinLength(3)]
    public string Name { get; set; } = null!;

    public Task RenameFolder(IFolder folder)
    {
        return folder.Rename(Name);
    }
}
