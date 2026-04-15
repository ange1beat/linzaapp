import React from "react";

import i18next from "i18next";

import SwitcherLanguage, {
  languagesArray,
} from "@/entities/language/ui/switcherLanguage";
import Button from "@/shared/ui/button";

import styles from "./TriggerSwitcherNotAuth.module.scss";

export default function TriggerSwitcherNotAuth() {
  const [currentLang, setCurrentLang] = React.useState(i18next.language);

  const onUpdateLanguage = (lang: string) => {
    setCurrentLang(lang);
  };

  return (
    <div className={styles["trigger-switcher"]}>
      <SwitcherLanguage onChangeLanguage={onUpdateLanguage}>
        <Button
          view="normal"
          iconLeft={
            languagesArray.find((langObj) => langObj.value === currentLang)
              ?.icon
          }
          className={styles["trigger-switcher__button"]}
        />
      </SwitcherLanguage>
    </div>
  );
}
