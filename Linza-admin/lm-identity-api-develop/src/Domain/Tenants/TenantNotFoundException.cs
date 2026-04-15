using System.Globalization;

namespace Domain.Tenants;

public class TenantNotFoundException : Exception
{
    private const string ErrorMessage = "Tenant '{0}' is not found";

    public TenantNotFoundException(string tenantId) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMessage, tenantId))
    {
    }
}
