import React from "react";

import { Person } from "@gravity-ui/icons";
import { ArrowRightFromSquare } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";

import { defaultAva } from "@/entities/members";
import { ROUTES } from "@/shared/config/routes";
import { Button, Link, Skeleton, Text } from "@/shared/ui";

import styles from "./UserModalEntity.module.scss";

interface IUserModalEntityProps {
  isLoad: boolean;
  avatar?: string | null;
  firstName: string;
  lastName: string;
  email: string;
  onOpenProfile: () => void;
  onLogout: () => void;
  actions?: React.ReactNode[];
}

function UserModalEntity({
  isLoad,
  avatar,
  firstName,
  lastName,
  email,
  onLogout,
  actions,
  onOpenProfile,
}: IUserModalEntityProps) {
  const { t } = useTranslation("entities.userModal");

  return (
    <div className={styles["user-modal"]}>
      <div className={styles["user-modal__modal-header"]} />
      <div className={styles["user-modal__user-info"]}>
        <img
          className={styles["user-modal__avatar"]}
          src={avatar || defaultAva}
          alt={t("avatar")}
        />
      </div>
      <div className={styles["user-modal__text-info"]}>
        <Skeleton isLoad={isLoad} height={24}>
          <Text
            ellipsis
            variant="modal-name"
            className={styles["user-modal__name"]}
          >
            {firstName} {lastName}
          </Text>
        </Skeleton>
        <Skeleton isLoad={isLoad} height={16}>
          <Text
            ellipsis
            variant="modal-email"
            className={styles["user-modal__email"]}
          >
            {email}
          </Text>
        </Skeleton>
      </div>
      <div className={styles["user-modal__buttons"]}>
        <Link href={ROUTES.profile} className={styles["user-modal__link"]}>
          <Button
            className={styles["user-modal__button"]}
            onClick={onOpenProfile}
            width="max"
            view="normal"
            size="l"
            iconLeft={<Icon data={Person} size={18} />}
          >
            <span className={styles["user-modal__button-text"]}>
              {t("profile")}
            </span>
          </Button>
        </Link>
        {actions}
        <Button
          className={styles["user-modal__button"]}
          width="max"
          view="normal"
          onClick={onLogout}
          size="l"
          iconLeft={<Icon data={ArrowRightFromSquare} size={18} />}
        >
          <span className={styles["user-modal__button-text"]}>
            {t("logOut")}
          </span>
        </Button>
      </div>
    </div>
  );
}

export default UserModalEntity;
