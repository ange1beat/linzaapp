import React from "react";

import { Power } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";

import { ISource } from "@/entities/sources/models/types";
import { Button, useAlert } from "@/shared/ui";

import { useToggleParsingDataSource } from "../../api/queries";

import styles from "./SourceStatusControl.module.scss";

interface IProps {
  source: ISource;
}

function SourceStatusControlFeature({ source }: IProps) {
  const { t } = useTranslation("feature.sourceStatusControl");
  const { addAlert } = useAlert();
  const toggleParsingDataSourceMutation = useToggleParsingDataSource();
  const toggleParsingHandler = () =>
    toggleParsingDataSourceMutation
      .mutateAsync({
        dataSourceId: source.id,
        isActive: !source.isActive,
      })
      .catch((err) => {
        if (err.status === 400) {
          addAlert({
            title: t("error-title"),
            message: t(err.errors.isActive),
            theme: "danger",
          });
        } else {
          addAlert({
            title: t("error-title"),
            message: t("server-error"),
            theme: "danger",
          });
        }
      });

  return (
    <Button
      view={source.isActive ? "action" : "normal"}
      loading={toggleParsingDataSourceMutation.isPending}
      onClick={toggleParsingHandler}
      size="s"
      className={styles["toggle-button"]}
      iconLeft={<Icon data={Power} size={16} />}
    />
  );
}

export default SourceStatusControlFeature;
