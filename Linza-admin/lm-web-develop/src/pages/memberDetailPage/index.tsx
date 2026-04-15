import React from "react";

import { TrashBin } from "@gravity-ui/icons";
import { Loader } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate } from "react-router-dom";

import { defaultAva, useGetMemberQuery } from "@/entities/members";
import { useTenantNameQuery } from "@/entities/tenant";
import { MemberDelete } from "@/features/memberDelete";
import { MemberManagementProject } from "@/features/memberManagementProject";
import { MemberRoleSelect } from "@/features/memberRole";
import { ROUTES } from "@/shared/config";
import { getFullName, getTelegramLink } from "@/shared/lib";
import { phoneNumberFormatter } from "@/shared/lib/phoneNumber";
import { Button, Layout, Link, Skeleton, Text } from "@/shared/ui";

import styles from "./MemberDetailPage.module.scss";

function MemberDetailPage() {
  const { t } = useTranslation("pages.memberDetailPage");
  const navigate = useNavigate();
  const { memberId } = useParams();
  const { isPending, selectedMember: member } = useGetMemberQuery(memberId!);
  const { isPending: isTenantNamePending, name: tenantName } =
    useTenantNameQuery();

  const fullName = getFullName({
    firstName: member.firstName,
    lastName: member.lastName,
  });

  const [isDeleteOpen, setIsDeleteOpen] = React.useState<boolean>(false);

  const breadCrumbsItems = [
    {
      text: tenantName,
      link: ROUTES.members,
      isPending: isTenantNamePending,
    },
    {
      text: t("member"),
      link: "/",
    },
  ];
  const onDeleteSuccess = () => {
    navigate(ROUTES.members);
  };
  return (
    <div className={styles["member-detail-page"]}>
      <Layout items={breadCrumbsItems}>
        <MemberDelete
          member={member}
          onCancel={() => setIsDeleteOpen(false)}
          onSuccess={onDeleteSuccess}
          isOpen={isDeleteOpen}
        />
        <div className={styles["member-detail-page__header"]}>
          <div className={styles["member-detail-page__info"]}>
            {isPending ? (
              <Loader
                className={styles["member-detail-page__avatar_loader"]}
                size="l"
              />
            ) : (
              <img
                className={styles["member-detail-page__avatar"]}
                src={member.avatarUrl || defaultAva}
                alt="avatar"
              />
            )}

            <div className={styles["member-detail-page__details"]}>
              <div className={styles["member-detail-page__details_row"]}>
                <Skeleton
                  isLoad={isPending}
                  height={36}
                  className={
                    styles["member-detail-page__details_name-skeleton"]
                  }
                >
                  <Text variant="display-1">{fullName}</Text>
                </Skeleton>
                <MemberRoleSelect member={member} />
              </div>

              <div className={styles["member-detail-page__details_row"]}>
                <Skeleton
                  isLoad={isPending}
                  height={24}
                  className={styles["member-detail-page__details_row-skeleton"]}
                >
                  <Text variant="body-3">{member.email}</Text>
                </Skeleton>
                <Skeleton
                  isLoad={isPending}
                  height={24}
                  className={styles["member-detail-page__details_row-skeleton"]}
                >
                  {member.telegramUsername && (
                    <Link
                      className={"details__telegram-link"}
                      href={getTelegramLink(member.telegramUsername)}
                      target="_blank"
                    >
                      <Text variant="body-3">{member.telegramUsername}</Text>
                    </Link>
                  )}
                </Skeleton>
                <Skeleton
                  isLoad={isPending}
                  height={24}
                  className={styles["member-detail-page__details_row-skeleton"]}
                >
                  <Text variant="body-3">
                    {member.phoneNumber
                      ? phoneNumberFormatter(member.phoneNumber).phone
                      : ""}
                  </Text>
                </Skeleton>
              </div>
            </div>
          </div>
          <Button
            view="normal"
            iconLeft={<TrashBin />}
            onClick={() => setIsDeleteOpen(true)}
          >
            {t("delete")}
          </Button>
        </div>
        <MemberManagementProject
          memberId={member.id}
          className={styles["member-detail-page__table"]}
        />
      </Layout>
    </div>
  );
}

export default MemberDetailPage;
