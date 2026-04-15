import React from "react";

import { useTranslation } from "react-i18next";

import { isSupervisor, useGetMemberQuery } from "@/entities/members";
import {
  ProjectsListEntity,
  useManageProjectsMembership,
  useProjectsOfMemberQuery,
} from "@/entities/projects";
import { useAlert } from "@/shared/ui";

function MemberManagementProject({
  memberId,
  className,
}: {
  memberId: string;
  className?: string;
}) {
  const { t } = useTranslation("errors");
  const { addAlert } = useAlert();

  const memberQuery = useGetMemberQuery(memberId);
  const { projects } = useProjectsOfMemberQuery(memberId);
  const modifyProjectMutation = useManageProjectsMembership(memberId);

  const onSelectHandler = (projectId: string) =>
    modifyProjectMutation
      .mutateAsync({
        userId: memberId,
        projectIds: [projectId],
        operation: "AddProjects",
      })
      .catch(() => {
        addAlert({
          title: t("title"),
          message: t("server-error"),
          theme: "danger",
        });
      });

  const onDeselectHandler = (projectId: string) =>
    modifyProjectMutation
      .mutateAsync({
        userId: memberId,
        projectIds: [projectId],
        operation: "RemoveProjects",
      })
      .catch(() => {
        addAlert({
          title: t("title"),
          message: t("server-error"),
          theme: "danger",
        });
      });

  return (
    <ProjectsListEntity
      className={className}
      selected={projects.projectIds}
      isDisabled={isSupervisor(memberQuery.selectedMember)}
      onSelect={onSelectHandler}
      onDeselect={onDeselectHandler}
    />
  );
}

export default MemberManagementProject;
