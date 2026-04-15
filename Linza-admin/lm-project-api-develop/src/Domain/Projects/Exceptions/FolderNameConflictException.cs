namespace Domain.Projects.Exceptions;

public class FolderNameConflictException : Exception
{
    private new const string Message = "Folder name must be unique!";

    public FolderNameConflictException() : base(Message)
    {
    }
}
