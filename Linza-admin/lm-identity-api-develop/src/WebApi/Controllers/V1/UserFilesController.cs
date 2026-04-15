using Asp.Versioning;
using Domain.Files;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.StaticFiles;

namespace WebApi.Controllers.V1;

[ApiController]
[ApiVersion("1.0")]
[Route("v{version:apiVersion}/users/files")]
public class UserFilesController : ControllerBase
{
    private const string FileNotFoundMsg = "File is not found";

    private readonly IFileStorage _fileStorage;

    public UserFilesController(IFileStorage fileStorage)
    {
        _fileStorage = fileStorage;
    }

    [AllowAnonymous]
    [HttpGet("{scope}/{name}")]
    [ResponseCache(Duration = 86400, Location = ResponseCacheLocation.Client)]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> GetFile(
        [FromRoute] string scope,
        [FromRoute] string name)
    {
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
