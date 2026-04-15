import { useTranslation } from "react-i18next";

const lngForBack: { [key: string]: string } = {
  en: "en-GB",
  ru: "ru",
};

const lngForFront: { [key: string]: string } = {
  "en-GB": "en",
  ru: "ru",
};

export function useBackLng(): string {
  const { i18n } = useTranslation();
  return lngForBack[i18n.language] || i18n.language;
}

export function backLngToFront(lng: string) {
  return lngForFront[lng] || lng;
}
