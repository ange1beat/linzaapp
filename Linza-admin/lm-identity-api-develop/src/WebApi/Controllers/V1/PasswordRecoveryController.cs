using Asp.Versioning;
using Domain.Auth.Exceptions;
using Domain.Auth.Recovery;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Requests.Auth.Recovery.Password;
using WebApi.Models.Responses.Auth;

namespace WebApi.Controllers.V1;

[ApiController]
[ApiVersion("1.0")]
[Route("v{version:apiVersion}/auth/recovery/password")]
[ProducesResponseType(StatusCodes.Status500InternalServerError)]
public class PasswordRecoveryController : ControllerBase
{
    private readonly IPasswordRecoveryCodes _codes;
    private readonly IPasswordRecovery _recovery;

    public PasswordRecoveryController(
        IPasswordRecoveryCodes codes,
        IPasswordRecovery recovery)
    {
        _codes = codes;
        _recovery = recovery;
    }

    [HttpPost("challenge/email")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ChallengeByEmail(
        [FromBody] EmailChallengeRequest request)
    {
        try
        {
            await request.SendCode(_codes);

            return NoContent();
        }
        catch (UnsupportedCultureException)
        {
            ModelState.AddModelError(
                nameof(request.Language),
                "Unsupported language"
            );

            return ValidationProblem(ModelState);
        }
    }

    [HttpPost("challenge/sms")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ChallengeBySms(
        [FromBody] SmsChallengeRequest request)
    {
        try
        {
            await request.SendCode(_codes);

            return NoContent();
        }
        catch (UnsupportedCultureException)
        {
            ModelState.AddModelError(
                nameof(request.Language),
                "Unsupported language"
            );

            return ValidationProblem(ModelState);
        }
    }

    [HttpPost("verify")]
    [ProducesResponseType(
        StatusCodes.Status200OK,
        Type = typeof(PasswordRecoveryTokenResponse)
    )]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> GetRecoveryToken(
        [FromBody] GetRecoveryTokenRequest request)
    {
        return Ok(new PasswordRecoveryTokenResponse(
            await request.RecoveryToken(_recovery)
        ));
    }

    [HttpPost("reset")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ResetPassword(
        [FromBody] ResetPasswordRequest request)
    {
        await request.ResetPassword(_recovery);

        return NoContent();
    }
}
