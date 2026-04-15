using Domain.Files;

namespace Provider.FileSystem;

public class FileSystemStorage : IFileStorage
{
    private readonly IFsStorageSettings _settings;

    public FileSystemStorage(IFsStorageSettings settings)
    {
        _settings = settings;
    }

    public Uri FileUri(string scope, string name)
    {
        return _settings.FileUri(scope, name);
    }

    public async Task Upload(string scope, string name, Stream fileContent)
    {
        string directory = _settings.Directory(scope);
        string filePath = Path.Combine(directory, name);

        if (System.IO.File.Exists(filePath))
        {
            throw new InvalidOperationException(
                $"File - '{name}' already exists in scope - '{scope}'"
            );
        }

        if (directory.Length > 0)
        {
            Directory.CreateDirectory(directory);
        }

        await using var fileStream = new FileStream(filePath, FileMode.Create);

        await fileContent.CopyToAsync(fileStream);
    }

    public Task<IFile> File(string scope, string name)
    {
        string directory = _settings.Directory(scope);
        string filePath = Path.Combine(directory, name);

        return Task.FromResult<IFile>(new FsFile(scope, filePath));
    }

    public Task Remove(string scope, params string[] names)
    {
        string directory = _settings.Directory(scope);

        foreach (var name in names)
        {
            string filePath = Path.Combine(directory, name);

            if (System.IO.File.Exists(filePath))
            {
                System.IO.File.Delete(filePath);
            }
        }

        return Task.CompletedTask;
    }
}
