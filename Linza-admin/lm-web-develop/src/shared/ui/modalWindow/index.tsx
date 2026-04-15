import React from "react";

import { Modal as GModal } from "@gravity-ui/uikit";

import Text from "../text";

import styles from "./ModalWindow.module.scss";

interface IModalProps {
  isOpen: boolean;
  children: React.ReactNode;
  title: string;
  onClose: () => void;
}

function ModalWindow({ isOpen, children, title, onClose }: IModalProps) {
  return (
    <GModal
      open={isOpen}
      onClose={onClose}
      contentClassName={styles["modal-window"]}
    >
      <Text variant="subheader-3" className={styles["modal-window__title"]}>
        {title}
      </Text>
      {children}
    </GModal>
  );
}

export default ModalWindow;
