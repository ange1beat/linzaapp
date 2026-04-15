import React from "react";

import cn from "classnames";
import classNames from "classnames";
import { useTranslation } from "react-i18next";

import { defaultProjectAvatar, IProject } from "@/entities/projects";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import {
  InputSearch,
  Pagination,
  Persona,
  Skeleton,
  Checkbox,
  Text,
  TableLayout,
} from "@/shared/ui";

import { useProjectsQuery } from "../../api/queries";

import styles from "./ProjectsListEntity.module.scss";

function ProjectRow({
  project,
  isSelected,
  isDisabled,
  onDeselect,
  onSelect,
}: {
  project: Pick<IProject, "id" | "avatarUrl" | "name">;
  isSelected: boolean;
  isDisabled: boolean;
  onSelect: (id: string) => void;
  onDeselect: (id: string) => void;
}) {
  const classes = cn(styles["project-list__row"], {
    [styles["--active"]]: isSelected,
  });
  return (
    <div className={classes} key={project.id}>
      <Checkbox
        size="m"
        checked={isSelected}
        disabled={isDisabled}
        onChange={() => {
          if (isSelected) {
            onDeselect(project.id);
          } else {
            onSelect(project.id);
          }
        }}
      />
      <Persona
        text={project.name}
        image={project.avatarUrl}
        defaultImage={defaultProjectAvatar}
        size="xxs"
      />
    </div>
  );
}

function ProjectsListEntity({
  selected,
  isDisabled,
  onSelect,
  onDeselect,
  className,
}: {
  selected: string[];
  isDisabled: boolean;
  onSelect: (id: string) => void;
  onDeselect: (id: string) => void;
  className?: string;
}) {
  const { t } = useTranslation("entities.projectsList");
  const [search, setSearch] = React.useState<string>("");
  const [page, setPage] = React.useState<number>(1);
  const [pageSize, setPageSize] = React.useState<number>(PAGE_SIZE);
  const selectedItems = new Set(selected);
  const classes = classNames(styles["project-list__list"], className);

  const { projects, total, isPending } = useProjectsQuery(
    search,
    page,
    pageSize,
  );

  const onSearchChange = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPage(p);
    setPageSize(pSize);
  };

  return (
    <div className={classes}>
      <TableLayout>
        <TableLayout.Header>
          <InputSearch
            onSearchChange={onSearchChange}
            placeholder={t("placeholder")}
            size="l"
            autoFocus
          />
        </TableLayout.Header>

        <TableLayout.Body>
          <Skeleton isLoad={isPending} height={500}>
            {projects.length > 0 ? (
              projects.map((project) => (
                <ProjectRow
                  key={project.id}
                  project={project}
                  isSelected={selectedItems.has(project.id)}
                  isDisabled={isDisabled}
                  onSelect={onSelect}
                  onDeselect={onDeselect}
                />
              ))
            ) : (
              <div className={styles["project-list__empty"]}>
                <Text variant="modal-email">{t("empty-message-search")}</Text>
              </div>
            )}
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
    </div>
  );
}

export default ProjectsListEntity;
