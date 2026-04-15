namespace WebApi.Models.Responses;

public class ProjectNameConflictResponse : ConflictResponse
{
    public override string Code => "project_name_conflict";

    public override string Message => "Project name is already used. Please use a different name.";
}
