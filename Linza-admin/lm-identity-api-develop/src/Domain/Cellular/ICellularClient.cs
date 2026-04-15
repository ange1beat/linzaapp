namespace Domain.Cellular;

public interface ICellularClient
{
    Task Send(SmsMessage message);
}
