namespace Domain.Cellular;

// ToDo: remove test impl. form Domain
public class TestCellularClient : ICellularClient
{
    public Task Send(SmsMessage message)
    {
        return Task.CompletedTask;
    }
}
