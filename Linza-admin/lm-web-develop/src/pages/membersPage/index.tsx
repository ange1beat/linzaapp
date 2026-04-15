import React from "react";

import { Plus } from "@gravity-ui/icons";
import { useTranslation } from "react-i18next";

import { TableMember, IMember } from "@/entities/members";
import { useTenantNameQuery } from "@/entities/tenant";
import { useUserQuery } from "@/entities/user";
import { MemberAdd } from "@/features/memberAdd";
import { MemberDelete } from "@/features/memberDelete";
import { ROUTES } from "@/shared/config";
import { Button, Layout, DropdownMenu, IDropdownMenuItem } from "@/shared/ui";

function MembersPage() {
  const tenant = useTenantNameQuery();
  const { user } = useUserQuery();
  const { t } = useTranslation("pages.membersPage");
  const [memberData, setMemberData] = React.useState<IMember>({} as IMember);
  const [isOpenDelete, setIsOpenDelete] = React.useState(false);

  const rowActions = (member: IMember): IDropdownMenuItem[] => {
    return [
      {
        text: t("delete"),
        action: (e) => {
          e.stopPropagation();
          setMemberData(member);
          setIsOpenDelete(true);
        },
        theme: "danger",
      },
    ];
  };

  const breadCrumbsItems = [
    {
      text: tenant.name,
      link: ROUTES.members,
      isPending: tenant.isPending,
    },
  ];

  const getRowActions = (member: IMember) => {
    if (member.id === user.id) {
      return <div />;
    }
    return <DropdownMenu items={rowActions(member)} />;
  };

  const headerActions = (
    <MemberAdd>
      <Button size="l" view="normal" iconLeft={<Plus />}>
        {t("invite")}
      </Button>
    </MemberAdd>
  );

  return (
    <>
      <Layout items={breadCrumbsItems}>
        <TableMember rowActions={getRowActions} headerActions={headerActions} />
      </Layout>
      <MemberDelete
        isOpen={isOpenDelete}
        member={memberData}
        onSuccess={() => setIsOpenDelete(false)}
        onCancel={() => setIsOpenDelete(false)}
      />
    </>
  );
}

export default MembersPage;
