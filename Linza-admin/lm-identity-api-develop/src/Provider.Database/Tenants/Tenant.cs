using Domain.Media;
using Domain.Tenants;

namespace Provider.Database.Tenants;

internal sealed class Tenant : ITenant
{
    public string Id => _entity.Id;

    private readonly DbTenant _entity;

    public Tenant(DbTenant entity)
    {
        _entity = entity;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.Id);
        media.Write("Name", _entity.Name);
    }
}
