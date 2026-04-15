import { z } from "zod";

export const schemaDefaults = <Schema extends z.ZodFirstPartySchemaTypes>(
  schema: Schema,
): z.TypeOf<Schema> => {
  const typeName = schema._def.typeName;
  if (typeName === z.ZodFirstPartyTypeKind.ZodDefault) {
    return schema._def.defaultValue();
  }
  if (typeName === z.ZodFirstPartyTypeKind.ZodObject) {
    return Object.fromEntries(
      Object.entries((schema as z.SomeZodObject).shape).map(([key, value]) => [
        key,
        schemaDefaults(value),
      ]),
    );
  }
  if (typeName === z.ZodFirstPartyTypeKind.ZodString) {
    return "";
  }
  if (typeName === z.ZodFirstPartyTypeKind.ZodNull) {
    return null;
  }
  if (typeName === z.ZodFirstPartyTypeKind.ZodNullable) {
    return null;
  }
  throw new Error(`Unsupported type ${schema._type}`);
};
