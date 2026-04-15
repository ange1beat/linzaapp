// using Domain.Auth.AuthManagers;
// using Domain.Auth.Tokens;
// using System.ComponentModel.DataAnnotations;
//
// namespace WebApi.Models.Requests.Auth;
//
// public class AuthTokenRequest : IValidatableObject
// {
//     [Required]
//     public AuthGrantType GrantType { get; set; }
//
//     public string StateToken { get; set; } = string.Empty;
//
//     public string RefreshToken { get; set; } = string.Empty;
//
//     public enum AuthGrantType
//     {
//         StateToken,
//         RefreshToken
//     }
//
//     public IEnumerable<ValidationResult> Validate(ValidationContext ctx)
//     {
//         if (GrantType == AuthGrantType.StateToken && string.IsNullOrEmpty(StateToken))
//         {
//             yield return new ValidationResult(
//                 $"The {nameof(StateToken)} field is required.",
//                 new[] { nameof(StateToken) }
//             );
//         }
//
//         if (GrantType == AuthGrantType.RefreshToken && string.IsNullOrEmpty(RefreshToken))
//         {
//             yield return new ValidationResult(
//                 $"The {nameof(RefreshToken)} field is required.",
//                 new[] { nameof(RefreshToken) }
//             );
//         }
//     }
//
//     public Task<IAuthToken> AuthToken(ITokens tokens)
//     {
//         return GrantType switch
//         {
//             AuthGrantType.StateToken   => tokens.Token(StateToken),
//             AuthGrantType.RefreshToken => tokens.Token(RefreshToken),
//
//             _ => throw new InvalidOperationException("Unknown grant type")
//         };
//     }
// }
