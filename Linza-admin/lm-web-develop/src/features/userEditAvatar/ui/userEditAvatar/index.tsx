import React from "react";

import { useTranslation } from "react-i18next";

import { defaultAva } from "@/entities/members";
import { useUploadAvatar } from "@/features/userEditAvatar/api/queries";
import { avatarValidationSchema } from "@/shared/models/avatar";
import { Avatar, useAlert } from "@/shared/ui";

interface IUserEditAvatar {
  avatar?: string;
}
function UserEditAvatar({ avatar }: IUserEditAvatar) {
  const { t } = useTranslation(["features.userEditAvatar", "controls"]);
  const uploadAvatarMutation = useUploadAvatar();
  const [error, setError] = React.useState<string | undefined>("");

  const { addAlert } = useAlert();
  const updateUserAvatar = (file: Blob) => {
    const isValidCroppedImage = avatarValidationSchema.safeParse(file);
    if (isValidCroppedImage.success) {
      setError("");
      const formData = new FormData();
      formData.append("image", file);
      uploadAvatarMutation
        .mutateAsync(formData)
        .then(() => {
          addAlert({
            title: t("successAvatarTitle"),
            theme: "success",
            message: t("successAvatarMessage"),
          });
        })
        .catch((response) => {
          if (response.status == 400) {
            setError(response.errors.errors.file[0]);
          } else {
            addAlert({
              title: t("errorAvatarTitle"),
              message: t("errorAvatarMessage"),
              theme: "danger",
            });
          }
        });
    } else {
      setError(isValidCroppedImage.error.errors[0].message);
    }
  };
  return (
    <Avatar
      avatar={avatar}
      onChange={updateUserAvatar}
      error={error}
      isLoad={uploadAvatarMutation.isPending}
      disabled={uploadAvatarMutation.isPending}
      defaultAva={defaultAva}
    />
  );
}

export default UserEditAvatar;
