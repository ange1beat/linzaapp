using Domain.Exceptions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using WebApi.Extensions.Environments;
using WebApi.Models.Responses;

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
            _ when IsError<UnauthorizedAccessException>(exc) => HandleUnauthorizedError,
            _ when IsError<AccessDeniedException>(exc)       => HandleAccessDeniedError,
            _ when IsError<ConcurrencyException>(exc)        => HandleConcurrencyError,
            _                                                => HandleUnexpectedError
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
        _logger.LogWarning(context.Exception, context.Exception.Message);

        context.Result = new ForbidResult();
    }

    private static void HandleConcurrencyError(ExceptionContext context)
    {
        context.Result = new ConflictObjectResult(new ConflictResponse
        {
            Code = "concurrency_conflict",
            Message = "The resource has been modified by another client. " +
                "Please refresh and try again."
        });
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
