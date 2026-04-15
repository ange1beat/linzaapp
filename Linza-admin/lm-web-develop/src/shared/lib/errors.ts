import { TFunction } from "i18next";

function flatErrors<T extends Record<string, string[]>>(
  errors: T,
): { [K in keyof T]: string } {
  const errorsResult: { [K in keyof T]: string } = {} as {
    [K in keyof T]: string;
  };
  for (const field in errors) {
    errorsResult[field] = errors[field][0];
  }
  return errorsResult;
}

function translateErrors<T>(
  errors: { [K in keyof T]: string },
  t: TFunction<string, undefined>,
) {
  const result = {} as { [K in keyof T]: string };
  for (const field in errors) {
    result[field] = t(errors[field]);
  }
  return result;
}

export { flatErrors, translateErrors };
