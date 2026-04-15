import { useTranslation } from "react-i18next";

export function GetFullName(user: { firstName: string; lastName: string }) {
  const { t } = useTranslation("errors");
  if (!user.firstName && !user.lastName) {
    return t("user.nameless");
  }
  return `${user.firstName} ${user.lastName}`;
}
