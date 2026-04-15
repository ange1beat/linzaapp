import React from "react";

import { useTranslation } from "react-i18next";

import { getRole, IMember } from "@/entities/members";
import { USER_ROLES } from "@/shared/config";
import { Select, useAlert } from "@/shared/ui";

import { useMemberRoleMutation } from "../../api/queries";

function MemberRoleSelect({
  className,
  member,
}: {
  className?: string;
  member: Pick<IMember, "id" | "roles">;
}) {
  const { t } = useTranslation(["errors"]);
  const { addAlert } = useAlert();
  const memberRoleMutation = useMemberRoleMutation();

  const onChangeHandler = (option: { value: string; label: string }) => {
    const isSupervisor = option.value === USER_ROLES.Supervisor;
    memberRoleMutation
      .mutateAsync({
        memberId: member.id,
        isSupervisor,
      })
      .catch(() => {
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("server-error", { ns: "errors" }),
          theme: "danger",
        });
      });
  };

  const options = Object.entries(USER_ROLES).map(([key, value]) => ({
    value: value,
    label: key,
  }));
  const value = getRole(member);
  return (
    <Select
      disabled={memberRoleMutation.isPending}
      className={className}
      value={value}
      options={options}
      onChange={onChangeHandler}
    />
  );
}

export default MemberRoleSelect;
