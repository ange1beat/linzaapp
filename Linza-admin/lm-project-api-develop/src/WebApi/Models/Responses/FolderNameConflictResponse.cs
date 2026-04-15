namespace WebApi.Models.Responses;

public class FolderNameConflictResponse : ConflictResponse
{
    public override string Code => "folder_name_conflict";

    public override string Message => "Folder name is already used. Please use a different name.";
}
