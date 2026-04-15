import { useTranslation } from "react-i18next";

import { useFavProjectsQuery } from "@/entities/projects";
import { Favorite, useAlert } from "@/shared/ui";

import {
  useAddProjectFavMutation,
  useDelProjectFavMutation,
} from "../../api/queries";

function FavoriteProject({
  isFavorite,
  projectId,
}: {
  isFavorite: boolean;
  projectId: string;
}) {
  const { t } = useTranslation(["errors"]);
  const addProjectFavMutation = useAddProjectFavMutation();
  const delProjectFavMutation = useDelProjectFavMutation();
  const favProjectsQuery = useFavProjectsQuery();
  const { addAlert } = useAlert();

  const favCount = favProjectsQuery.projects.length;

  const onClickHandler = () => {
    if (isFavorite) {
      delProjectFavMutation.mutateAsync(projectId).catch(() => {
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("server-error", { ns: "errors" }),
          theme: "danger",
        });
      });
    } else {
      if (favCount === 10) {
        addAlert({
          title: t("title", { ns: "errors" }),
          message: t("project.max-fav", { ns: "errors" }),
          theme: "danger",
        });
      } else {
        addProjectFavMutation.mutateAsync(projectId).catch(() => {
          addAlert({
            title: t("title", { ns: "errors" }),
            message: t("server-error", { ns: "errors" }),
            theme: "danger",
          });
        });
      }
    }
  };

  return <Favorite isSelected={isFavorite} onClick={onClickHandler} />;
}

export default FavoriteProject;
