import React from "react";

import cn from "classnames";
import { useTranslation } from "react-i18next";

import {
  defaultAva,
  IMember,
  isSupervisor,
  useMembersQuery,
} from "@/entities/members";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import {
  Checkbox,
  InputSearch,
  Pagination,
  Persona,
  Skeleton,
  TableLayout,
  Text,
} from "@/shared/ui";

import styles from "./MembersListEntity.module.scss";

function MemberListContent({
  member,
  selectedItems,
  onDeselect,
  onSelect,
}: {
  member: Pick<
    IMember,
    "id" | "firstName" | "lastName" | "avatarUrl" | "roles"
  >;
  selectedItems: Set<string>;
  onSelect: (id: string) => void;
  onDeselect: (id: string) => void;
}) {
  const isSelected = selectedItems.has(member.id);
  const isDisabled = isSupervisor(member);
  const classes = cn(styles["members-list__row"], {
    [styles["members-list__row--active"]]: isSelected,
  });
  return (
    <div className={classes} key={member.id}>
      <Checkbox
        size="m"
        checked={isSelected}
        disabled={isDisabled}
        onChange={() => {
          if (isSelected) {
            onDeselect(member.id);
          } else {
            onSelect(member.id);
          }
        }}
      />
      <Persona
        text={member.firstName.concat(" ", member.lastName)}
        image={member.avatarUrl}
        defaultImage={defaultAva}
        size="xxs"
      />
    </div>
  );
}

function MembersListEntity({
  selected,
  onSelect,
  onDeselect,
}: {
  selected: string[];
  onSelect: (id: string) => void;
  onDeselect: (id: string) => void;
}) {
  const { t } = useTranslation("entities.membersList");
  const [search, setSearch] = React.useState<string>("");
  const [page, setPage] = React.useState<number>(1);
  const [pageSize, setPageSize] = React.useState<number>(PAGE_SIZE);
  const selectedItems = new Set(selected);

  const { members, total, isPending } = useMembersQuery(search, pageSize, page);

  const onSearchChange = (value: string) => {
    setSearch(value);
    setPage(1);
  };

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPage(p);
    setPageSize(pSize);
  };
  return (
    <div className={styles["members-list__list"]}>
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
            {members.length > 0 ? (
              members.map((member) => (
                <MemberListContent
                  key={member.id}
                  member={member}
                  selectedItems={selectedItems}
                  onSelect={onSelect}
                  onDeselect={onDeselect}
                />
              ))
            ) : (
              <div className={styles["members-list__empty"]}>
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

MembersListEntity.defaultProps = {
  disabled: false,
};

export default MembersListEntity;
