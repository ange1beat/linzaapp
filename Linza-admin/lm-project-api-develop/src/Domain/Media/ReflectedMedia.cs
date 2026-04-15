using System.Collections;
using System.Reflection;
using System.Runtime.Serialization;

namespace Domain.Media;

public abstract class ReflectedMedia : IMedia
{
    public virtual void Write<T>(string name, T value)
    {
        if (HasProperty(name) is false)
        {
            //No property found in the media.
            return;
        }

        var propertyInfo = PropertyInfo(name);
        if (propertyInfo.GetSetMethod() is null)
        {
            return;
        }

        if (IsSingleMedia(propertyInfo))
        {
            EnsureSingleMedia(propertyInfo, value);

            var instance = Activator.CreateInstance(propertyInfo.PropertyType) as IMedia;
            (value as IWritable)!.Write(instance!);
            propertyInfo.SetValue(this, instance, null);
        }
        else if (IsEnumerableMedia(propertyInfo))
        {
            var genericType = propertyInfo.PropertyType.GetGenericArguments()[0];
            var instance = (IList)Activator.CreateInstance(
                typeof(List<>).MakeGenericType(genericType)
            )!;

            foreach (var writable in (value as IEnumerable<IWritable>)!)
            {
                var mediaInstance = Activator.CreateInstance(genericType)!;
                writable.Write((mediaInstance as IMedia)!);
                instance.Add(mediaInstance);
            }

            propertyInfo.SetValue(this, instance, null);
        }
        else
        {
            //Non media types.
            propertyInfo.SetValue(this, value, null);
        }
    }

    private bool HasProperty(string name)
    {
        return GetType().GetProperties().Any(x =>
            x.Name.Equals(name, StringComparison.OrdinalIgnoreCase)
        );
    }

    private PropertyInfo PropertyInfo(string name)
    {
        return GetType().GetProperties().Single(x =>
            x.Name.Equals(name, StringComparison.OrdinalIgnoreCase)
        );
    }

    private static bool IsSingleMedia(PropertyInfo propertyInfo)
    {
        return typeof(IMedia).IsAssignableFrom(propertyInfo.PropertyType);
    }

    private static void EnsureSingleMedia<T>(PropertyInfo propertyInfo, T value)
    {
        if (value is ISerializable ^ typeof(IMedia).IsAssignableFrom(propertyInfo.PropertyType))
        {
            throw new InvalidOperationException(
                "Failed to write Media. Either property is not IMedia or the value is not ISerializable." +
                "Property name:" + propertyInfo.Name +
                "Property type:" + propertyInfo.PropertyType.Name +
                "Value type: " + typeof(T).Name);
        }
    }

    private static bool IsEnumerableMedia(PropertyInfo propertyInfo)
    {
        return typeof(IEnumerable<IMedia>).IsAssignableFrom(propertyInfo.PropertyType);
    }
}
