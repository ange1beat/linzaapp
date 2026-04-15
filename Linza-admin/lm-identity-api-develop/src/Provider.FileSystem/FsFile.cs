using Domain.Files;
using FileNotFoundException = Domain.Files.Exceptions.FileNotFoundException;

namespace Provider.FileSystem;

internal sealed class FsFile : IFile
{
    public string Name => Path.GetFileName(_path);

    public string Directory => Path.GetDirectoryName(_path) ?? string.Empty;

    public string Extension => Path.GetExtension(_path);

    private readonly string _scope;
    private readonly string _path;

    public FsFile(string scope, string path)
    {
        _scope = scope;
        _path = path;
    }

    public Stream Content()
    {
        try
        {
            return new FileStream(_path, FileMode.Open, FileAccess.Read);
        }
        catch (System.IO.FileNotFoundException)
        {
            throw new FileNotFoundException(_scope, Name);
        }
    }
}
