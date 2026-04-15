using Asp.Versioning;
using Domain.Files;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http.Extensions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.StaticFiles;
using WebApi.Models.Authentication.Guards;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects/files")]
public class FilesController : ApiControllerBase
{
    private const string FileNotFoundMsg = "File is not found";

    private readonly IFileStorage _fileStorage;
    private readonly IResourceGuard _guard;

    public FilesController(IFileStorage fileStorage, IResourceGuard guard)
    {
        _fileStorage = fileStorage;
        _guard = guard;
    }

    [AllowAnonymous]
    [HttpGet("{scope}/{name}")]
    [ResponseCache(Duration = 86400, Location = ResponseCacheLocation.Client)]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetFile(
        [FromRoute] string scope,
        [FromRoute] string name)
    {
        if (!_guard.IsUrlValid(Request.GetEncodedUrl()))
        {
            return Unauthorized();
        }

        try
        {
            IFile file = await _fileStorage.File(scope, name);

            var typeProvider = new FileExtensionContentTypeProvider();
            if (!typeProvider.TryGetContentType(file.Name, out var contentType))
            {
                contentType = "application/octet-stream";
            }

            return new FileStreamResult(file.Content(), contentType);
        }
        catch (FileNotFoundException)
        {
            return NotFound(FileNotFoundMsg);
        }
    }
}
