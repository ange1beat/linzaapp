using Asp.Versioning;
using Domain.Auth;
using Domain.Auth.Exceptions;
using Domain.Auth.Factors;
using Domain.Auth.Tokens;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Net.Http.Headers;
using WebApi.Models.Auth;
using WebApi.Models.Requests.Auth;
using WebApi.Models.Responses.Auth;

namespace WebApi.Controllers.V1;

[ApiController]
[ApiVersion("1.0")]
[Produces("application/json")]
[Consumes("application/json")]
[Route("v{version:apiVersion}/auth")]
public class AuthController : ControllerBase
{
    private readonly IBaseAuth _baseAuth;
    private readonly IOtpAuthFactor _otpFactor;
    private readonly IAuthTokens _authTokens;

    public AuthController(
        IBaseAuth baseAuth,
        IOtpAuthFactor otpFactor,
        IAuthTokens authTokens)
    {
        _baseAuth = baseAuth;
        _otpFactor = otpFactor;
        _authTokens = authTokens;
    }

    [HttpPost("")]
    [ProducesResponseType<AuthStateResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> Authenticate([FromBody] AuthRequest request)
    {
        try
        {
            IAuthState state = await request.Authenticate(_baseAuth);

            var response = new AuthStateResponse();
            state.Write(response);

            return Ok(response);
        }
        catch (AccountLockedException exc)
        {
            Response.Headers.RetryAfter =
                HeaderUtilities.FormatDate(exc.LockoutEndDate);

            return Unauthorized();
        }
    }

    [HttpPost("factors/otp/challenge/email")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> ChallengeOtpByEmail(
        [FromBody] OtpFactorChallengeRequest request)
    {
        try
        {
            await request.ChallengeByEmail(_otpFactor);

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

    [HttpPost("factors/otp/challenge/sms")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> ChallengeOtpBySms(
        [FromBody] OtpFactorChallengeRequest request)
    {
        try
        {
            await request.ChallengeBySms(_otpFactor);

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

    [HttpPost("factors/otp/verify")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> VerifyOtpFactor(
        [FromBody] VerifyOtpFactorRequest request)
    {
        IAuthState state = await request.Verify(_otpFactor);

        var response = new AuthStateResponse();
        state.Write(response);

        return Ok(response);
    }

    [HttpPost("token")]
    [ProducesResponseType<AccessTokenResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> GetToken()
    {
        var refreshCookieCtx = new RefreshCookieContext();
        if (!refreshCookieCtx.Contains(Request))
        {
            return Unauthorized();
        }

        try
        {
            AuthToken token = await _authTokens.RefreshedToken(
                refreshCookieCtx.Value(Request)
            );

            refreshCookieCtx.Append(Response, token);

            return Ok(new AccessTokenResponse(token));
        }
        catch (UnauthorizedException)
        {
            refreshCookieCtx.Delete(Response);

            return Unauthorized();
        }
    }

    [HttpPost("sign-in")]
    [ProducesResponseType<AccessTokenResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> SignIn(
        [FromBody] SignInRequest request)
    {
        AuthToken token = await request.NewToken(_authTokens);

        new RefreshCookieContext().Append(Response, token);

        return Ok(new AccessTokenResponse(token));
    }

    [HttpPost("sign-out")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public new async Task<IActionResult> SignOut()
    {
        var refreshCookieCtx = new RefreshCookieContext();

        if (refreshCookieCtx.Contains(Request))
        {
            await _authTokens.RevokeRefreshToken(
                refreshCookieCtx.Value(Request)
            );

            refreshCookieCtx.Delete(Response);
        }

        return NoContent();
    }
}
