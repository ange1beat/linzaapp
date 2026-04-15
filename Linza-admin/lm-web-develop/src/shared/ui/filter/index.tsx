import React from "react";

import { ArrowRotateLeft, CaretDown, Funnel } from "@gravity-ui/icons";
import { Button as GButton, Icon } from "@gravity-ui/uikit";
import { Checkbox as GCheckbox } from "@gravity-ui/uikit";
import cn from "classnames";
import { useTranslation } from "react-i18next";

import Text from "@/shared/ui/text";

import SelectDropdown, { useSelectDropDown } from "../selectDropdown";

import styles from "./Filter.module.scss";

type IOptions = {
  value: string;
  label: string;
};

type IProps = {
  groups: {
    label: string;
    name: string;
    options: IOptions[];
  }[];
  value: { [k: string]: string[] };
  onChange: (v: { [k: string]: string[] }) => void;
};

function Filter({ value, groups, onChange }: IProps) {
  const { t } = useTranslation("shared.filter");
  const { isOpen, onToggle, ref } = useSelectDropDown();

  const classes = cn(styles["filter__btn"], {
    [styles["filter__btn-opened"]]: isOpen,
  });

  const handleChange = (groupName: string, optionValue: string) => {
    const updatedValue = { ...value };
    if (!updatedValue[groupName]) {
      updatedValue[groupName] = [];
    }

    if (updatedValue[groupName].includes(optionValue)) {
      updatedValue[groupName] = updatedValue[groupName].filter(
        (val) => val !== optionValue,
      );
    } else {
      updatedValue[groupName].push(optionValue);
    }

    onChange(updatedValue);
  };

  return (
    <div className={styles.wrapper}>
      <SelectDropdown
        isOpen={isOpen}
        onToggle={onToggle}
        switcher={
          <GButton size="l" selected={isOpen} className={classes}>
            <Icon data={Funnel} />
            {t("button-filter-title")}
            <Icon data={CaretDown} />
          </GButton>
        }
      >
        <div className={styles["filter__wrapper"]} ref={ref}>
          <div className={styles["filter__reset-wrapper"]}>
            <Text variant="filter">{t("title")}</Text>
            <GButton onClick={() => onChange({})}>
              <Icon data={ArrowRotateLeft} />
              {t("button-reset-title")}
            </GButton>
          </div>
          <div className={styles["filter__groups"]}>
            {groups.map((group) => (
              <div key={group.name}>
                <Text
                  variant="filter"
                  className={styles["filter__dropdown__group-header"]}
                >
                  {group.label}
                </Text>
                <div className={styles["filter__dropdown__checkbox-group"]}>
                  {group.options.map((option) => (
                    <GCheckbox
                      key={option.value}
                      size="l"
                      checked={
                        value[group.name]?.includes(option.value) || false
                      }
                      onChange={() => handleChange(group.name, option.value)}
                      className={styles["filter__dropdown__checkbox"]}
                    >
                      {option.label}
                    </GCheckbox>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </SelectDropdown>
    </div>
  );
}

export default Filter;
