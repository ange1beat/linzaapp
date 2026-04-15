import React from "react";

import BreadCrumbs from "@/shared/ui/breadCrumbs";

import styles from "./Layout.module.scss";

interface IBreadCrumbItems {
  text: string;
  link: string;
  isPending?: boolean;
}

interface ILayout {
  actions?: React.ReactNode;
  menu?: React.ReactNode;
  items: IBreadCrumbItems[];
}

function Layout(props: React.PropsWithChildren<ILayout>) {
  const Actions = () => {
    if (props.actions) {
      return <div className={styles["layout__actions"]}>{props.actions}</div>;
    }
    return null;
  };

  const Menu = () => {
    if (props.menu) {
      return <div className={styles["layout__menu"]}>{props.menu}</div>;
    }
  };

  return (
    <div className={styles.layout}>
      <div className={styles["layout__header"]}>
        <BreadCrumbs items={props.items} />
        <Actions />
      </div>
      <Menu />
      <div className={styles["layout__content"]}>{props.children}</div>
    </div>
  );
}

export default Layout;
