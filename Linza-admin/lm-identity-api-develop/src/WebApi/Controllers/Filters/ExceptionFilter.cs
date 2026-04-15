using Domain.Auth.Exceptions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using WebApi.Extensions.Environment;

namespace WebApi.Controllers.Filters;

public class ExceptionFilter : IExceptionFilter
{
    private readonly IHostEnvironment _env;
    private readonly ILogger<ExceptionFilter> _logger;

    public ExceptionFilter(IHostEnvironment env, ILogger<ExceptionFilter> logger)
    {
        _env = env;
        _logger = logger;
    }

    public void OnException(ExceptionContext context)
    {
        var exc = context.Exception;
        Action<ExceptionContext> handler = context switch
        {
            _ when IsError<UnauthorizedException>(exc) => HandleUnauthorizedError,
            _ when IsError<AccessDeniedException>(exc) => HandleAccessDeniedError,
            _ => HandleUnexpectedError
        };

        handler.Invoke(context);
    }

    private static bool IsError<T>(Exception exc) where T : Exception
    {
        Exception? currentExc = exc;
        while (currentExc is not null)
        {
            if (currentExc is T || currentExc.GetType().IsAssignableTo(typeof(T)))
            {
                return true;
            }

            currentExc = currentExc.InnerException;
        }

        return false;
    }

    private static void HandleUnauthorizedError(ExceptionContext context)
    {
        context.Result = new UnauthorizedResult();
    }

    private void HandleAccessDeniedError(ExceptionContext context)
    {
        context.Result = new ForbidResult();
    }

    private void HandleUnexpectedError(ExceptionContext context)
    {
        var exc = context.Exception;

        _logger.LogError(context.Exception, context.Exception.Message);

        dynamic response;

        if (_env.IsLocal() || _env.IsDevelopment())
        {
            response = new
            {
                Message = exc.Message,
                Details = exc.StackTrace
            };
        }
        else
        {
            response = new
            {
                Message = "Internal server error occurred. Please, try to again later."
            };
        }

        context.Result = new ObjectResult(response)
        {
            StatusCode = StatusCodes.Status500InternalServerError
        };
    }
}
