using Domain.Authentication;
using Domain.Projects.Membership;
using Domain.Users;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests;

public class PatchMembershipRequest : IValidatableObject
{
    [Required]
    public PatchOperation? Operation { get; set; } = null!;

    public IEnumerable<string> ProjectIds { get; set; } = Array.Empty<string>();

    public enum PatchOperation
    {
        AddProjects,
        RemoveProjects,
        RemoveAllProjects
    }

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (!ProjectIds.Any() &&
            Operation is PatchOperation.AddProjects or PatchOperation.RemoveProjects)
        {
            yield return new ValidationResult(
                "At least one project ID must be specified",
                new[] { nameof(ProjectIds) }
            );
        }
    }

    public async Task ApplyPatch(
        IProjectsMembership membership,
        IUser user,
        IUserIdentity requester)
    {
        Task task = Operation switch
        {
            PatchOperation.AddProjects       => membership.Assign(user, ProjectIds, requester),
            PatchOperation.RemoveProjects    => membership.Remove(user, ProjectIds, requester),
            PatchOperation.RemoveAllProjects => membership.Remove(user, requester),

            _ => throw new InvalidOperationException("Unknown operation")
        };

        await task;
    }
}
