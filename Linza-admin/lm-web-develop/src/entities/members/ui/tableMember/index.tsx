import React from "react";

import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import { defaultAva } from "@/entities/members";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS, ROUTES } from "@/shared/config";
import { formatISODateToCustomFormat, getTelegramLink } from "@/shared/lib";
import {
  Pagination,
  Persona,
  Table,
  TableLayout,
  Text,
  InputSearch,
  Link,
  LabelMemberRole,
} from "@/shared/ui";

import { useMembersQuery } from "../../api/queries";
import { getRole } from "../../lib/getRole";
import { IMember } from "../../models";

import styles from "./TableMember.module.scss";

type ITableMember = {
  rowActions: (member: IMember) => React.ReactNode;
  headerActions: React.ReactNode;
};

export default function TableMember({
  rowActions,
  headerActions,
}: ITableMember) {
  const { t } = useTranslation("entities.tableMember");
  const [pageNumber, setPageNumber] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(PAGE_SIZE);
  const [search, setSearch] = React.useState("");

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setPageNumber(1);
  };

  const membersData = useMembersQuery(search, pageSize, pageNumber);

  const navigate = useNavigate();

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
          size="xs"
          image={member.avatarUrl}
          defaultImage={defaultAva}
          text={member.firstName.concat(" ", member.lastName)}
          className={styles["member-table__persona"]}
        />
      ),
      className: styles["member-table__column"],
    },
    {
      id: "email",
      name: t("columns.email"),
      template: (member: IMember) => (
        <Text variant="body-short" className={styles["member-table__email"]}>
          {member.email}
        </Text>
      ),
      className: styles["member-table__column"],
    },
    {
      id: "phone",
      name: t("columns.phone"),
      template: (member: IMember) => (
        <Text variant="body-short">{member.phoneNumber}</Text>
      ),
      width: 160,
    },
    {
      id: "telegram",
      name: t("columns.telegram"),
      template: (member: IMember) => {
        {
          return member.telegramUsername ? (
            <Link
              href={getTelegramLink(member.telegramUsername)}
              target="_blank"
            >
              {member.telegramUsername}
            </Link>
          ) : (
            <></>
          );
        }
      },
    },
    {
      id: "role",
      name: t("columns.role"),
      template: (member: IMember) => <LabelMemberRole role={getRole(member)} />,
      width: 110,
    },
    {
      id: "lastLogin",
      name: t("columns.last-login"),
      template: (member: IMember) => {
        return (
          <Text variant="body-short">
            {member.lastLoginDate &&
              formatISODateToCustomFormat(member.lastLoginDate)}
          </Text>
        );
      },
      width: 140,
    },
    {
      id: "actions",
      name: "",
      template: (member: IMember) => rowActions(member),
      width: 60,
    },
  ];

  return (
    <TableLayout>
      <TableLayout.Header>
        <div className={styles["member-table__header"]}>
          <div className={styles["member-table__actions"]}>
            <InputSearch
              size="l"
              placeholder={t("searchPlaceholder")}
              autoFocus
              onSearchChange={handleSearchChange}
            />
            {headerActions}
          </div>
        </div>
      </TableLayout.Header>
      <TableLayout.Body>
        <Table
          className={styles["member-table__table"]}
          columns={columns}
          data={membersData.members}
          isLoad={membersData.isPending}
          onRowClick={(member) => navigate(ROUTES.memberDetail(member.id))}
        />
      </TableLayout.Body>
      <TableLayout.Footer>
        <Pagination
          total={membersData.total}
          page={pageNumber}
          pageSize={pageSize}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          onUpdate={paginationUpdateHandler}
        />
      </TableLayout.Footer>
    </TableLayout>
  );
}
