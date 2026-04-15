import React from "react";

import { PencilToLine, Plus } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { useUserQuery } from "@/entities/user/api/queries";
import { UserEditAvatar } from "@/features/userEditAvatar";
import { ROUTES } from "@/shared/config/routes";
import { getFullName } from "@/shared/lib";
import { phoneNumberFormatter } from "@/shared/lib/phoneNumber";
import { Button, Skeleton, Text } from "@/shared/ui";

import styles from "./ProfilePage.module.scss";

export default function ProfilePage() {
  const { t } = useTranslation("pages.profilePage");
  const { isPending, user } = useUserQuery();
  const fullName = getFullName({
    firstName: user.firstName,
    lastName: user.lastName,
  });
  return (
    <div className={styles["profile__page"]}>
      <div className={styles.profile}>
        <div className={styles["profile__section"]}>
          <UserEditAvatar />
        </div>
        <div className={styles["profile__section"]}>
          <div className={styles["section__value"]}>
            <Text variant="subheader-2">{t("name")}</Text>
            <Skeleton isLoad={isPending} height={20}>
              <Text className={styles["section__text"]} variant="body-2">
                {fullName}
              </Text>
            </Skeleton>
          </div>
          <Link to={ROUTES.profileName}>
            <Button
              className={styles["section__buttons"]}
              view="normal"
              size="m"
              disabled={isPending}
              iconLeft={<Icon data={PencilToLine} />}
            >
              {t("change")}
            </Button>
          </Link>
        </div>
        <div className={styles["profile__section"]}>
          <div className={styles["section__value"]}>
            <Text variant="subheader-2">{t("email")}</Text>
            <Skeleton isLoad={isPending} height={20}>
              <Text className={styles["section__text"]} variant="body-2">
                {user.email}
              </Text>
            </Skeleton>
          </div>
          <Link to={ROUTES.profileEmail}>
            <Button
              className={styles["section__buttons"]}
              view="normal"
              size="m"
              disabled={isPending}
              iconLeft={<Icon data={PencilToLine} />}
            >
              {t("change")}
            </Button>
          </Link>
        </div>
        <div className={styles["profile__section"]}>
          <div className={styles["section__value"]}>
            <Text variant="subheader-2"> {t("phone")}</Text>
            <Skeleton isLoad={isPending} height={20}>
              <Text
                className={
                  user.phoneNumber && user.phoneNumber.length > 0
                    ? styles["section__text"]
                    : styles["section__text-placeholder"]
                }
                variant="body-2"
              >
                {user.phoneNumber && user.phoneNumber.length > 0
                  ? phoneNumberFormatter(user.phoneNumber).phone
                  : t("none")}
              </Text>
            </Skeleton>
          </div>
          <Link to={ROUTES.profilePhone}>
            <Button
              className={styles["section__buttons"]}
              view="normal"
              size="m"
              disabled={isPending}
              iconLeft={
                user.phoneNumber && user.phoneNumber.length > 0 ? (
                  <Icon data={PencilToLine} />
                ) : (
                  <Icon data={Plus} />
                )
              }
            >
              {user.phoneNumber && user.phoneNumber.length > 0
                ? t("change")
                : t("add")}
            </Button>
          </Link>
        </div>
        <div className={styles["profile__section"]}>
          <div className={styles["section__value"]}>
            <Text variant="subheader-2">{t("telegram")}</Text>
            <Skeleton isLoad={isPending} height={20}>
              <Text
                className={
                  user.telegramUsername && user.telegramUsername.length > 0
                    ? styles["section__text"]
                    : styles["section__text-placeholder"]
                }
                variant="body-2"
              >
                {user.telegramUsername && user.telegramUsername.length > 0
                  ? user.telegramUsername
                  : t("none")}
              </Text>
            </Skeleton>
          </div>
          <Link to={ROUTES.profileTelegram}>
            <Button
              className={styles["section__buttons"]}
              view="normal"
              size="m"
              disabled={isPending}
              iconLeft={
                user.telegramUsername && user.telegramUsername.length > 0 ? (
                  <Icon data={PencilToLine} />
                ) : (
                  <Icon data={Plus} />
                )
              }
            >
              {user.telegramUsername && user.telegramUsername.length > 0
                ? t("change")
                : t("add")}
            </Button>
          </Link>
        </div>
        <div className={styles["profile__section"]}>
          <div className={styles["section__value"]}>
            <Text variant="subheader-2">{t("password")} </Text>
          </div>
          <Link to={ROUTES.profilePassword}>
            <Button
              className={styles["section__buttons"]}
              view="normal"
              size="m"
              disabled={isPending}
              iconLeft={<Icon data={PencilToLine} />}
            >
              {t("change")}
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
