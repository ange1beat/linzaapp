namespace Domain.Tenants;

public interface ITenants
{
    ITenantSearchQuery Search();

    Task<ITenant> Tenant(string tenantId);
}
