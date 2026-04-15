import { useTranslation } from "react-i18next";

import { IProject } from "@/entities/projects";
import { useAlert } from "@/shared/ui";
import InputConfirm from "@/shared/ui/inputConfirm";

import { useProjectNameMutation } from "../../api/queries";
import { useNameForm } from "../../models/forms";

function ProjectChangeName({
  className,
  loading,
  project,
}: {
  className?: string;
  loading?: string;
  project: Pick<IProject, "id" | "name">;
}) {
  const { t } = useTranslation(["errors"]);
  const projectNameMutation = useProjectNameMutation();
  const { addAlert } = useAlert();
  const { handleSubmit, nameField, setError, errors } = useNameForm(
    project.name,
  );

  const onChangeHandler = handleSubmit(({ name }) => {
    projectNameMutation
      .mutateAsync({ id: project.id, name })
      .catch((response) => {
        if (response.status === 400) {
          setError("name", {
            type: "custom",
            message: response.errors.name,
          });
        }
        if (response.status === 409) {
          setError("name", {
            type: "custom",
            message: "project.conflict-project-name-error",
          });
        } else {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        }
      });
  });

  const isLoading = !!loading || projectNameMutation.isPending;
  return (
    <InputConfirm
      className={className}
      value={project.name}
      loading={isLoading}
      isError={!!errors.name}
      errorMessage={t(errors.name?.message ?? "", { ns: "errors" })}
      onChange={nameField.onChange}
      onApply={() => onChangeHandler()}
    />
  );
}

export default ProjectChangeName;
