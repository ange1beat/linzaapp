import React from "react";

import { Magnifier } from "@gravity-ui/icons";
import { useTranslation } from "react-i18next";

import { defaultAva } from "@/entities/members";
import { useGetProjectMembersQuery } from "@/entities/members/api/queries";
import { IMember } from "@/entities/members/models/models";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import { getFullName } from "@/shared/lib";
import {
  Input,
  Pagination,
  Persona,
  TableLayout,
  Text,
  Link,
  LabelMemberRole,
} from "@/shared/ui";

import styles from "./ProjectMembersTable.module.scss";

interface IProjectMembersTable {
  projectId: string;
  rowActions: (member: IMember) => React.ReactNode;
  headActions: React.ReactNode;
}

function ProjectMembersTable({
  projectId,
  rowActions,
  headActions,
}: IProjectMembersTable) {
  const { t } = useTranslation("entities.projectMembersTable");
  const [pageNumber, setPageNumber] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(PAGE_SIZE);
  const [search, setSearch] = React.useState("");

  const projectMembersData = useGetProjectMembersQuery(projectId);

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPageNumber(p);
    setPageSize(pSize);
  };
  const columns = [
    {
      id: "person",
      name: t("columns.person"),
      template: (member: IMember) => (
        <Persona
          size="s"
          image={member.avatarUrl}
          text={getFullName({
            firstName: member.firstName,
            lastName: member.lastName,
          })}
          defaultImage={defaultAva}
        />
      ),
    },
    {
      id: "email",
      name: t("columns.email"),
      template: (member: IMember) => (
        <Text variant="body-short">{member.email}</Text>
      ),
    },
    {
      id: "phone",
      name: t("columns.phone"),
      template: (member: IMember) => (
        <Text variant="body-short">{member.phoneNumber}</Text>
      ),
    },
    {
      id: "telegram",
      name: t("columns.telegram"),
      template: (member: IMember) => {
        return (
          member.telegramUsername && (
            <Link href={`https://t.me/${member.telegramUsername.slice(1)}`}>
              {member.telegramUsername}
            </Link>
          )
        );
      },
    },
    {
      id: "role",
      name: t("columns.role"),
      template: (member: IMember) => <LabelMemberRole role={member.roles[0]} />,
    },
    {
      id: "actions",
      name: t("columns.action"),
      template: (member: IMember) => rowActions(member),
    },
  ];
  return (
    <>
      <TableLayout>
        <TableLayout.Header>
          <div className={styles["project-members-table__header"]}>
            <Text variant="header-1">{t("title")}</Text>
            <div className={styles["project-members-table__actions"]}>
              <Input
                size="l"
                value={search}
                onChange={setSearch}
                placeholder={t("searchPlaceholder")}
                rightContent={
                  <Magnifier
                    className={styles["project-members-table__icon"]}
                  />
                }
              />
              {headActions}
            </div>
          </div>
        </TableLayout.Header>
        <TableLayout.Body>
          {JSON.stringify(columns)}
          {/*<Table*/}
          {/*  className={styles["project-members-table__table"]}*/}
          {/*  columns={columns}*/}
          {/*  data={projectMembersData.members}*/}
          {/*  isLoad={projectMembersData.isPending}*/}
          {/*/>*/}
        </TableLayout.Body>
        <TableLayout.Footer>
          <Pagination
            total={projectMembersData.total}
            page={pageNumber}
            pageSize={pageSize}
            pageSizeOptions={PAGE_SIZE_OPTIONS}
            onUpdate={paginationUpdateHandler}
          />
        </TableLayout.Footer>
      </TableLayout>
    </>
  );
}

export default ProjectMembersTable;
