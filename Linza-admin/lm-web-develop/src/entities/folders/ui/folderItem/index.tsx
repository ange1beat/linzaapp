import React from "react";

import { TrashBin } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";

import { ROUTES } from "@/shared/config";
import { Link, Text } from "@/shared/ui";

import FolderImg from "../../media/folder.svg";
import { IFolder } from "../../models";

import styles from "./FolderItem.module.scss";

function FolderItem({
  folder,
  onDelete,
  projectId,
}: {
  folder: IFolder;
  onDelete: (folder: IFolder) => void;
  projectId: string;
}) {
  return (
    <Link
      href={ROUTES.folder(projectId, folder.id)}
      className={styles["folder-item"]}
    >
      <div
        className={styles["folder-item__delete-button"]}
        onClick={(e) => {
          e.preventDefault();
          onDelete(folder);
        }}
      >
        <Icon
          data={TrashBin}
          size={16}
          className={styles["folder-item__trash"]}
        />
      </div>
      <img
        className={styles["folder-item__folder-img"]}
        src={FolderImg}
        alt={folder.name}
      />
      <Text variant="body-1" className={styles["folder-item__text"]}>
        {folder.name}
      </Text>
    </Link>
  );
}

export default FolderItem;
