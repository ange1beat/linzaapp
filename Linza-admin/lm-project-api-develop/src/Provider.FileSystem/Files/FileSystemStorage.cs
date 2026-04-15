using Domain.Files;

namespace Provider.FileSystem.Files;

public class FileSystemStorage : IFileStorage
{
    private readonly IFsStorageSettings _settings;

    public FileSystemStorage(IFsStorageSettings settings)
    {
        _settings = settings;
    }

    public Uri FileUri(string scope, string filename)
    {
        return _settings.FileUri(scope, filename);
    }

    public async Task Upload(string scope, string filename, Stream fileContent)
    {
        string directory = _settings.Directory(scope);
        string filePath = Path.Combine(directory, filename);

        if (System.IO.File.Exists(filePath))
        {
            throw new InvalidOperationException(
                $"File - '{filename}' already exists in scope - '{scope}'"
            );
        }

        if (directory.Length > 0)
        {
            Directory.CreateDirectory(directory);
        }

        await using var fileStream = new FileStream(filePath, FileMode.Create);

        await fileContent.CopyToAsync(fileStream);
    }

    public Task<IFile> File(string scope, string filename)
    {
        string directory = _settings.Directory(scope);
        string filePath = Path.Combine(directory, filename);

        return Task.FromResult<IFile>(new FsFile(scope, filePath));
    }

    public Task Remove(string scope, string filename)
    {
        string directory = _settings.Directory(scope);
        string filePath = Path.Combine(directory, filename);

        if (System.IO.File.Exists(filePath))
        {
            System.IO.File.Delete(filePath);
        }

        return Task.CompletedTask;
    }
}
