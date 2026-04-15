namespace WebApi.Models.Authentication.Guards;

public interface IResourceGuard
{
    Uri SignedUrl(Uri url);

    Uri SignedUrl(string url);

    bool IsUrlValid(Uri url);

    bool IsUrlValid(string url);
}
