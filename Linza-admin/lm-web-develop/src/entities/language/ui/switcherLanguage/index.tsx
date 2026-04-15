import React from "react";

import { SelectDropdown, useSelectDropDown, Text } from "@/shared/ui";

import { EnIcon } from "../../icons/enIcon";
import { RuIcon } from "../../icons/ruIcon";
import { switchLng } from "../../lib/switchLng";

import styles from "./SwitcherLanguage.module.scss";

type ISwitcher = {
  onChangeLanguage?: (lang: string) => void;
};

type ILanguage = {
  icon: React.ReactNode;
  label: string;
  value: string;
};

type IMenuProps = {
  onClick: (lang: string) => void;
};

export const languagesArray: ILanguage[] = [
  {
    icon: <RuIcon />,
    label: "Русский",
    value: "ru",
  },
  {
    icon: <EnIcon />,
    label: "English",
    value: "en",
  },
];

function MenuLanguage(props: IMenuProps) {
  return (
    <ul className={styles.languages}>
      {languagesArray.map((lang) => (
        <li
          key={lang.value}
          className={styles["languages__element"]}
          onClick={() => props.onClick(lang.value)}
        >
          {lang.icon}
          <Text variant="body-2">{lang.label}</Text>
        </li>
      ))}
    </ul>
  );
}

export default function SwitcherLanguage(
  props: React.PropsWithChildren<ISwitcher>,
) {
  const { isOpen, onToggle, ref } = useSelectDropDown();

  const switchLanguage = (lang: string) => {
    switchLng(lang);
    props.onChangeLanguage?.(lang);
  };

  return (
    <SelectDropdown
      ref={ref}
      isOpen={isOpen}
      onToggle={onToggle}
      switcher={props.children}
      side="right"
    >
      <MenuLanguage onClick={switchLanguage} />
    </SelectDropdown>
  );
}
