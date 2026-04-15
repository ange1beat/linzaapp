import { SubmitHandler, useController, useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";

import { Button, Text } from "@/shared/ui";
import Avatar from "@/shared/ui/avatar";
import Input from "@/shared/ui/input";
import ModalWindow from "@/shared/ui/modalWindow";

import styles from "./EditProjectFormEntity.module.scss";

interface IProject {
  name: string;
  avatarUrl: string;
}

interface IProps {
  data: IProject;
  onChange: (data: IProject) => void;
  onSuccess: (data: IProject) => void;
  onCancel: () => void;
  errors: IProject;
  isLoad: boolean;
}

function EditProjectFormEntity({
  data,
  onSuccess,
  onCancel,
  onChange,
  errors,
  isLoad,
}: IProps) {
  const { t } = useTranslation("entities.editProjectForm");
  const { handleSubmit, control, watch } = useForm<IProject>({});
  const submit: SubmitHandler<IProject> = (projectData) =>
    onSuccess(projectData);
  const { field: name } = useController({
    control: control,
    name: "name",
    defaultValue: data.name,
  });
  const { field: avatar } = useController({
    control: control,
    name: "avatarUrl",
    defaultValue: data.avatarUrl,
  });

  const onChangeHandler = () => {
    const value = watch();
    onChange(value);
  };

  return (
    <ModalWindow isOpen title={t("modal-title")} onClose={onCancel}>
      <form
        className={styles["edit-project-form"]}
        onSubmit={handleSubmit(submit)}
        onChange={onChangeHandler}
      >
        <Avatar
          avatar={data.avatarUrl}
          defaultAva=""
          onChange={avatar.onChange}
        />
        {errors.avatarUrl && (
          <Text
            variant="body-2"
            className={styles["edit-project-form__avatar-error"]}
          >
            {errors.avatarUrl}
          </Text>
        )}
        <div className={styles["edit-project-form__project-name"]}>
          <Text variant="body-2">{t("project-name-title")}</Text>
          <Input
            size="l"
            onChange={name.onChange}
            value={name.value}
            errorMessage={errors.name}
            isError={!!errors.name}
            placeholder={t("project-name-input-placeholder")}
            disabled={name.disabled || isLoad}
            ref={name.ref}
          />
        </div>
        <div className={styles["edit-project-form__buttons"]}>
          <Button size="l" view="normal" onClick={onCancel} loading={isLoad}>
            {t("cancel-btn")}
          </Button>
          <Button size="l" view="action" type="submit" loading={isLoad}>
            {t("apply-btn")}
          </Button>
        </div>
      </form>
    </ModalWindow>
  );
}

export default EditProjectFormEntity;
