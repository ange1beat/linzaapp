import React from "react";

import { useTranslation } from "react-i18next";

import {
  defaultProjectAvatar,
  IProject,
  useProjectAvatarMutation,
} from "@/entities/projects";
import { avatarValidationSchema } from "@/shared/models/avatar";
import { Avatar } from "@/shared/ui";

function ProjectChangeAvatar({
  project,
}: {
  project: Pick<IProject, "avatarUrl" | "id">;
}) {
  const { t } = useTranslation("errors");
  const newAvatar = new FormData();
  const [error, setError] = React.useState<string>("");
  const projectAvatarMutation = useProjectAvatarMutation();
  const onChangeAvatar = (blob: Blob) => {
    const isValidCroppedImage = avatarValidationSchema.safeParse(blob);
    if (isValidCroppedImage.success) {
      newAvatar.append("file", blob);
      setError("");
      projectAvatarMutation
        .mutateAsync({
          projectId: project.id,
          avatar: newAvatar,
        })
        .then(() => {
          newAvatar.delete("file");
        })
        .catch(async (response) => {
          if (response.status === 400) {
            setError(response.errors.errors.file);
          } else {
            setError("avatar.unexpected-error-avatar");
          }
        });
    } else {
      setError(isValidCroppedImage.error.errors[0].message);
    }
  };
  return (
    <Avatar
      avatar={project.avatarUrl}
      onChange={onChangeAvatar}
      defaultAva={defaultProjectAvatar}
      isLoad={projectAvatarMutation.isPending}
      error={t(error)}
    />
  );
}

export default ProjectChangeAvatar;
