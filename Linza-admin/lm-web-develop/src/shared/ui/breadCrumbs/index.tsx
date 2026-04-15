import React from "react";

import {
  Breadcrumbs as GBreadCrumbs,
  FirstDisplayedItemsCount,
  LastDisplayedItemsCount,
} from "@gravity-ui/uikit";
import cn from "classnames";
import { useTranslation } from "react-i18next";

import { Link, Text } from "@/shared/ui";

import styles from "./BreadCrumbs.module.scss";

interface IBreadCrumbItems {
  text: string;
  link: string;
  isPending?: boolean;
}

interface IProps {
  items: IBreadCrumbItems[];
}

function BreadCrumbs({ items }: IProps) {
  const { t } = useTranslation("shared.breadCrumbs");
  const itemsWithDefaultAction = items.map((item) => ({
    ...item,
    action: () => {},
  }));
  return (
    <GBreadCrumbs
      items={itemsWithDefaultAction}
      lastDisplayedItemsCount={LastDisplayedItemsCount.One}
      firstDisplayedItemsCount={FirstDisplayedItemsCount.One}
      renderItemContent={(item, isCurrent) => {
        const classes = cn(styles["breadcrumbs__text"], {
          [styles["--active"]]: isCurrent,
        });
        return isCurrent ? (
          <Text variant="header-1">
            {item.isPending ? t("load-name") : item.text}
          </Text>
        ) : (
          <Link className={styles["breadcrumbs__link"]} href={item.link}>
            <Text variant="header-1" className={classes}>
              {item.isPending ? t("load-name") : item.text}
            </Text>
          </Link>
        );
      }}
      renderItemDivider={() => (
        <Text variant="header-1" className={styles["breadcrumbs__divider"]}>
          /
        </Text>
      )}
    />
  );
}

export default BreadCrumbs;
