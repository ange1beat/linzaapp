using Domain.Media;

namespace Domain.Tenants;

public interface ITenant : IWritable
{
    string Id { get; }
}
