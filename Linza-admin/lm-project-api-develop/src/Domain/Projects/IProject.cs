using Domain.Media;
using Domain.Projects.Folders;

namespace Domain.Projects;

public interface IProject : IWritable
{
    string Id { get; }

    IProjectFolders Folders();

    IProjectMembers Members();

    Task Rename(string name);

    Task AttachAvatar(Stream content, string extension);

    Task RemoveAvatar();
}
