import { configure } from "@gravity-ui/uikit";
import i18next from "i18next";

import { updLanguage } from "../models/stores";

type LngList = "ru" | "en";

export function switchLng(lng: string) {
  i18next.changeLanguage(lng);
  configure({
    lang: lng as LngList,
  });
  updLanguage(lng);
}
