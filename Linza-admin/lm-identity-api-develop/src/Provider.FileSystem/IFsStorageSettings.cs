namespace Provider.FileSystem;

public interface IFsStorageSettings
{
    Uri FileUri(string scope, string name);

    string Directory(string scope);
}
