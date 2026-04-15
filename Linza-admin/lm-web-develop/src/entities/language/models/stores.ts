import { create } from "zustand";
import { persist } from "zustand/middleware";

import { getURLParams } from "@/shared/lib";

import { backLngToFront } from "../lib/backLng";

type LanguageState = {
  language: string;
  updateLanguage: (newLanguage: string) => void;
};

const languageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: "ru",
      updateLanguage: (language) => set({ language }),
    }),
    {
      name: "language",
    },
  ),
);

export const getLanguage = () => {
  let lng = getURLParams("language");
  lng = lng && backLngToFront(lng);
  return lng || languageStore.getState().language;
};

export const updLanguage = (newLanguage: string) =>
  languageStore.getState().updateLanguage(newLanguage);
