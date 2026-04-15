import React from "react";

import { useTranslation } from "react-i18next";

import { IFolder } from "@/entities/folders";
import { useFoldersQuery } from "@/entities/folders/api/queries";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import {
  InputSearch,
  Pagination,
  Skeleton,
  TableLayout,
  Text,
} from "@/shared/ui";

import FolderItem from "../folderItem";

import styles from "./FoldersList.module.scss";

function FoldersList({
  addAction,
  deleteAction,
  projectId,
}: {
  addAction: React.ReactNode;
  deleteAction: (folder: IFolder) => void;
  projectId: string;
}) {
  const { t } = useTranslation("entities.foldersList");
  const [name, setName] = React.useState<string>("");
  const [page, setPage] = React.useState<number>(1);
  const [pageSize, setPageSize] = React.useState<number>(PAGE_SIZE);
  const { folders, total, isPending } = useFoldersQuery(
    projectId,
    page,
    pageSize,
    name,
  );

  const onSearchChange = (value: string) => {
    setName(value);
    setPage(1);
  };

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPage(p);
    setPageSize(pSize);
  };
  return (
    <TableLayout>
      <TableLayout.Header>
        <div className={styles["folders-list__header"]}>
          <InputSearch
            onSearchChange={onSearchChange}
            placeholder={t("placeholder")}
            size="l"
            autoFocus
          />
          {addAction}
        </div>
      </TableLayout.Header>

      <TableLayout.Body>
        <Skeleton isLoad={isPending} height={500}>
          <div className={styles["folders-list__list"]}>
            {folders.length > 0 ? (
              folders.map((folder) => (
                <FolderItem
                  key={folder.id}
                  folder={folder}
                  onDelete={deleteAction}
                  projectId={projectId}
                />
              ))
            ) : (
              <div className={styles["folders-list__empty"]}>
                <Text variant="modal-email">{t("empty-message-search")}</Text>
              </div>
            )}
          </div>
        </Skeleton>
      </TableLayout.Body>
      <TableLayout.Footer>
        <Pagination
          total={total}
          page={page}
          pageSize={pageSize}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          onUpdate={paginationUpdateHandler}
        />
      </TableLayout.Footer>
    </TableLayout>
  );
}

export default FoldersList;
