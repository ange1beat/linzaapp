using Provider.Database.Projects.Favorites;
using WebApi.Models.Settings;

namespace WebApi.Models.Projects;

public class FavoritesSettings : ConfigSettingsBase, IFavoritesSettings
{
    private const string Section = "Application:Projects:Favorites";

    public int MaxSize => MandatoryValue<int>("MaxSize");

    public FavoritesSettings(IConfiguration config) : base(config, Section)
    {
    }
}
