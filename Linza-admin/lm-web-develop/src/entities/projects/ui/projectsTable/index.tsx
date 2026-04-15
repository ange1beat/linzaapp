import React, { ReactNode, useState } from "react";

import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { defaultProjectAvatar } from "@/entities/projects";
import { IProject } from "@/entities/projects/models";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import { ROUTES } from "@/shared/config/routes";
import { formatISODateToCustomFormat } from "@/shared/lib";
import {
  TableLayout,
  Pagination,
  Table,
  Persona,
  Text,
  InputSearch,
} from "@/shared/ui";

import { useFavProjectsQuery, useProjectsQuery } from "../../api/queries";

import styles from "./ProjectsTable.module.scss";

function ProjectsTable({
  rowActions,
  headerActions,
  favoriteProject,
  createdBy,
}: {
  rowActions: (project: IProject) => ReactNode;
  headerActions: ReactNode;
  createdBy: (userId: string) => ReactNode;
  favoriteProject: (isFavorite: boolean, projectId: string) => ReactNode;
}) {
  const { t } = useTranslation("entities.projectsTable");
  const [search, setSearch] = useState("");
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE);
  const projectsQuery = useProjectsQuery(search, pageNumber, pageSize);
  const favProjectsQuery = useFavProjectsQuery();
  const favIds = new Set(favProjectsQuery.projects.map((p) => p.id));

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setPageNumber(1);
  };

  const columns = [
    {
      id: "favorite",
      name: t("favorite"),
      width: 70,
      align: "center",
      template: (p: IProject) => (
        <div className={styles["projects-table__favorite"]}>
          {favoriteProject(favIds.has(p.id), p.id)}
        </div>
      ),
    },
    {
      id: "project-name",
      name: t("project"),
      template: (p: IProject) => (
        <Link to={ROUTES.project(p.id)}>
          <Persona
            size="xs"
            image={p.avatarUrl}
            defaultImage={defaultProjectAvatar}
            text={p.name}
          />
        </Link>
      ),
    },
    {
      id: "project-creator",
      name: t("creator"),
      template: (item: IProject) => createdBy(item.createdBy),
    },
    {
      id: "project-creation",
      name: t("creation"),
      width: 140,
      template: (item: IProject) => (
        <Text variant="body-short">
          {formatISODateToCustomFormat(item.createdAt)}
        </Text>
      ),
    },
    {
      id: "project-action",
      name: "",
      width: 100,
      template: (p: IProject) => (
        <div className={styles["projects-table__actions"]}>{rowActions(p)}</div>
      ),
    },
  ];

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPageNumber(p);
    setPageSize(pSize);
  };

  return (
    <TableLayout>
      <TableLayout.Header>
        <div className={styles["projects-table__header"]}>
          <InputSearch
            size="l"
            placeholder={t("search-placeholder")}
            autoFocus
            onSearchChange={handleSearchChange}
          />
          {headerActions}
        </div>
      </TableLayout.Header>
      <TableLayout.Body>
        <Table
          className={styles["projects-table__table"]}
          columns={columns}
          data={projectsQuery.projects}
          isLoad={projectsQuery.isPending}
          pageSize={pageSize}
        />
      </TableLayout.Body>
      <TableLayout.Footer>
        <Pagination
          total={projectsQuery.total}
          page={pageNumber}
          pageSize={pageSize}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          onUpdate={paginationUpdateHandler}
        />
      </TableLayout.Footer>
    </TableLayout>
  );
}

export default ProjectsTable;
