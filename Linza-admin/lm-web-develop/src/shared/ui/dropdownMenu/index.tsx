import React from "react";

import { Ellipsis } from "@gravity-ui/icons";
import {
  DropdownMenu as GDropDownMenu,
  Icon,
  DropdownMenuItem,
} from "@gravity-ui/uikit";

import styles from "./DropdownMenu.module.scss";

export interface IDropdownMenuItem {
  text: React.ReactNode;
  theme?: "danger" | "normal";
  disabled?: boolean;
  action?: (e: React.MouseEvent) => void;
  items?: IDropdownMenuItem[];
}

interface IDropdownMenu {
  items: IDropdownMenuItem[];
}

function DropdownMenu({ items }: IDropdownMenu) {
  const onClickHandler = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
  };

  return (
    <GDropDownMenu
      items={items as DropdownMenuItem[]}
      icon={<Icon data={Ellipsis} className={styles["dropdown-menu__icon"]} />}
      onSwitcherClick={onClickHandler}
    />
  );
}

export default DropdownMenu;
