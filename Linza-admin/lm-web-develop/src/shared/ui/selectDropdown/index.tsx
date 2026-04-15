import React, { forwardRef } from "react";

import classNames from "classnames";

import { useClickAway } from "../../hooks/useClickAway";

import styles from "./SelectDropdown.module.scss";

interface ISelectDropdownProps {
  children: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
  switcher: React.ReactNode;
  side?: "right" | "left";
}

function SelectDropdown(
  { isOpen, children, onToggle, switcher, side }: ISelectDropdownProps,
  ref: React.Ref<HTMLDivElement>,
) {
  const classDropdownList = classNames({
    [styles["dropdown__list--right"]]: !side || side === "right",
    [styles["dropdown__list--left"]]: side && side === "left",
  });
  return (
    <div className={styles.dropdown}>
      <div onClick={onToggle}>{switcher}</div>
      {isOpen && (
        <div className={classDropdownList} ref={ref}>
          {children}
        </div>
      )}
    </div>
  );
}

export default forwardRef(SelectDropdown);

export function useSelectDropDown() {
  const [isOpen, setIsOpen] = React.useState(false);
  const ref = useClickAway<HTMLDivElement>(() => {
    setIsOpen(false);
  });
  const onClose = () => {
    setIsOpen(false);
  };
  const onOpen = () => {
    setIsOpen(true);
  };
  const onToggle = () => {
    setIsOpen((prevState) => !prevState);
  };
  return { isOpen, onOpen, onClose, onToggle, ref };
}
