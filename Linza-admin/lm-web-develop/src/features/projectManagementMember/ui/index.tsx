import { useTranslation } from "react-i18next";

import {
  useAddMembersToProjectMutation,
  useDeleteMemberFromProjectMutation,
  useGetProjectMembersQuery,
} from "@/entities/members";
import MembersListEntity from "@/entities/members/ui/membersList";
import { useAlert } from "@/shared/ui";

function ProjectManagementMember({ projectId }: { projectId: string }) {
  const { t } = useTranslation("errors");
  const { addAlert } = useAlert();

  const { membersIds } = useGetProjectMembersQuery(projectId);
  const addMembersToProjectMutation = useAddMembersToProjectMutation(projectId);
  const deleteMemberFromProjectMutation =
    useDeleteMemberFromProjectMutation(projectId);

  const onSelectHandler = (memberId: string) =>
    addMembersToProjectMutation
      .mutateAsync({
        projectId: projectId,
        userIds: [memberId],
      })
      .catch(() => {
        addAlert({
          title: t("title"),
          message: t("server-error"),
          theme: "danger",
        });
      });

  const onDeselectHandler = (memberId: string) =>
    deleteMemberFromProjectMutation
      .mutateAsync({
        projectId: projectId,
        userId: memberId,
      })
      .catch(() => {
        addAlert({
          title: t("title"),
          message: t("server-error"),
          theme: "danger",
        });
      });

  return (
    <MembersListEntity
      selected={membersIds}
      onSelect={onSelectHandler}
      onDeselect={onDeselectHandler}
    />
  );
}

export default ProjectManagementMember;
