import React from "react";

import { Flag } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import cn from "classnames";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import SwitcherLanguage from "@/entities/language/ui/switcherLanguage";
import { delToken, useRevokeTokenMutation } from "@/entities/session";
import { UserModal, UserMenuItem, useUserQuery } from "@/entities/user";
import { ROUTES } from "@/shared/config";
import { useClickAway } from "@/shared/hooks";
import Button from "@/shared/ui/button";

import styles from "./UserModalWindow.module.scss";

function UserModalWindow({ isSelected }: { isSelected: boolean }) {
  const { t } = useTranslation("features.modalWindow");
  const [isShow, setIsShow] = React.useState(false);
  const { isPending, user } = useUserQuery();
  const revokeTokenMutation = useRevokeTokenMutation();
  const ref = useClickAway<HTMLDivElement>(() => {
    setIsShow(false);
  });
  const navigate = useNavigate();

  const logoutHandler = () => {
    revokeTokenMutation.mutateAsync().finally(() => {
      delToken();
      navigate(ROUTES.login);
    });
  };

  const classes = cn(styles["user-modal-window"], {
    [styles["user-modal-window--show-window"]]: isShow,
  });
  return (
    <div className={classes}>
      <UserMenuItem
        isSelected={isSelected}
        avatar={user.avatarUrl}
        onMouseDown={(e) => e.stopPropagation()}
        onTouchStart={(e) => e.stopPropagation()}
        onClick={() => {
          setIsShow((prevState) => !prevState);
        }}
      />
      {isShow && (
        <div ref={ref} className={styles["user-modal-window__window"]}>
          <UserModal
            firstName={user.firstName}
            lastName={user.lastName}
            email={user.email}
            avatar={user.avatarUrl}
            isLoad={isPending}
            onOpenProfile={() => setIsShow(false)}
            onLogout={logoutHandler}
            actions={[
              <SwitcherLanguage key={"switcher-language"}>
                <Button
                  className={styles["user-modal__button"]}
                  width="max"
                  view="normal"
                  size="l"
                  iconLeft={<Icon data={Flag} size={18} />}
                >
                  <span className={styles["user-modal__button-text"]}>
                    {t("changeLanguage")}
                  </span>
                </Button>
              </SwitcherLanguage>,
            ]}
          />
        </div>
      )}
    </div>
  );
}

export default UserModalWindow;
