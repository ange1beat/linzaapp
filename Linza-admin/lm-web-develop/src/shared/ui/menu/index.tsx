import React from "react";

import { Button } from "@gravity-ui/uikit";
import cn from "classnames";
import { useLocation } from "react-router";
import { Link } from "react-router-dom";

import styles from "./Menu.module.scss";

function Menu({
  className,
  mainItems,
  secondaryItems,
}: {
  className?: string;
  mainItems: React.ReactNode;
  secondaryItems: React.ReactElement<typeof MenuItem>;
}) {
  const classes = cn(styles.menu, className);
  return (
    <nav className={classes}>
      <ul className={styles["menu__main-items"]}>{mainItems}</ul>
      <ul className={styles["menu__second-items"]}>{secondaryItems}</ul>
    </nav>
  );
}

function MenuItem({
  isSelected,
  children,
}: {
  isSelected: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const classes = cn(styles["menu-item"], {
    [styles["menu-item--selected"]]: isSelected,
  });
  return (
    <li className={classes}>
      <div className={styles["menu-item__marker"]} />
      {children}
    </li>
  );
}

function MenuItemButton({
  isSelected,
  children,
  onClick,
}: {
  isSelected: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  return (
    <MenuItem isSelected={isSelected}>
      <Button className={styles["menu-item__button"]} onClick={onClick}>
        {children}
      </Button>
    </MenuItem>
  );
}

function MenuItemLink({
  children,
  link,
  end = false,
}: {
  link: string;
  children: React.ReactNode;
  end?: boolean;
}) {
  const { pathname } = useLocation();
  const endSlashPosition =
    link !== "/" && link.endsWith("/") ? link.length - 1 : link.length;
  const isActive =
    pathname === link ||
    (!end && pathname.startsWith(link) && pathname.charAt(endSlashPosition)) ===
      "/";

  return (
    <MenuItem isSelected={isActive}>
      <Link className={styles["menu-item__link"]} to={link}>
        <Button className={styles["menu-item__button"]}>{children}</Button>
      </Link>
    </MenuItem>
  );
}

Menu.MenuItemLink = MenuItemLink;
Menu.MenuItemButton = MenuItemButton;
Menu.MenuItem = MenuItem;

export default Menu;
