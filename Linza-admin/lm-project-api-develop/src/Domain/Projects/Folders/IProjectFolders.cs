namespace Domain.Projects.Folders;

public interface IProjectFolders
{
    IFolderSearchQuery SearchQuery();

    Task<IFolder> Folder(string id);

    Task<IFolder> NewFolder(string name);

    Task Remove(string id);
}
