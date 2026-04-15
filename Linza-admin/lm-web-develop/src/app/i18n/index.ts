import { configure } from "@gravity-ui/uikit";
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { getLanguage } from "@/entities/language/models/stores";

import controlsEN from "./en/controls.json";
import errorsEn from "./en/errors.json";
import controlsRu from "./ru/controls.json";
import errorsRu from "./ru/errors.json";

type LngList = "ru" | "en";

const translations = import.meta.glob("/src/**/*.json", { eager: true });

const resources: Record<string, Record<string, object>> = {};
const fileRegex =
  /\/src\/(?<slice>\w*)\/?.*\/(?<component>\w+)\/(?<language>\w+)\.json$/;

for (const path in translations) {
  const groups = path.match(fileRegex)?.groups;
  if (!groups) {
    continue;
  }
  const { slice, component, language } = groups;
  resources[language] = resources[language] || {};
  resources[language][`${slice}.${component}`] = (
    translations[path] as { default: object }
  ).default;
}

resources.ru.errors = errorsRu;
resources.en.errors = errorsEn;
resources.ru.controls = controlsRu;
resources.en.controls = controlsEN;

i18n.use(initReactI18next).init({
  lng: getLanguage(),
  fallbackLng: "en",
  resources,
  interpolation: {
    escapeValue: false,
  },
});

configure({
  lang: getLanguage() as LngList,
});
