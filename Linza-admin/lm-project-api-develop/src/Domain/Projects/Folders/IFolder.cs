using Domain.Media;

namespace Domain.Projects.Folders;

public interface IFolder : IWritable
{
    Task Rename(string name);
}
