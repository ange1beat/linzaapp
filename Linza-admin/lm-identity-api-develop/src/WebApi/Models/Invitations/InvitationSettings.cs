using Provider.Database.Users.Invitations;
using System.Globalization;
using System.Text.RegularExpressions;
using System.Xml;
using WebApi.Models.Configuration;

namespace WebApi.Models.Invitations;

public class InvitationSettings : IInvitationSettings
{
    private const string BaseSection = "Invitations";

    private static readonly Regex _queryParamRegex = new(@"\{(\w+)\}", RegexOptions.Compiled);

    public TimeSpan InvitationTtl => XmlConvert.ToTimeSpan(
        _appConfig.MandatoryValue<string>("InvitationTtl")
    );

    private readonly AppConfiguration _appConfig;

    public InvitationSettings(IConfiguration config)
        : this(new AppConfiguration(config, BaseSection))
    {
    }

    private InvitationSettings(AppConfiguration appConfig)
    {
        _appConfig = appConfig;
    }

    public Uri RegistrationLink(string invitationId, CultureInfo culture)
    {
        var urlTemplate = _appConfig.MandatoryValue<string>("RegistrationUrlTemplate");

        var queryParams = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { "invitationId", invitationId },
            { "language", culture.Name }
        };

        return new Uri(_queryParamRegex.Replace(
            urlTemplate,
            match => queryParams[match.Groups[1].Value]
        ));
    }
}
