import React from "react";

import { useTranslation } from "react-i18next";

import { Text } from "@/shared/ui";

import styles from "./PasswordRules.module.scss";

const validationRules = [
  { content: "uppercase" },
  { content: "numbers" },
  { content: "lowercase" },
  { content: "non-alphanumeric" },
];

function PasswordRules() {
  const { t } = useTranslation("entities.passwordRules");
  return (
    <div className={styles["validation-rules"]}>
      <Text
        variant="caption-2"
        className={styles["validation-rules__rules-text"]}
      >
        {t("rules.title")}
      </Text>
      <ol className={styles["validation-rules__rules-list"]}>
        {validationRules.map((rule) => (
          <li
            key={rule.content}
            className={styles["validation-rules__list-item"]}
          >
            <Text
              variant="caption-2"
              className={styles["validation-rules__rules-text"]}
            >
              {t(`rules.${rule.content}`)}
            </Text>
          </li>
        ))}
      </ol>
    </div>
  );
}

export default PasswordRules;
