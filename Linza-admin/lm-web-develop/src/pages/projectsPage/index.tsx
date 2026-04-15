import React from "react";

import { Plus } from "@gravity-ui/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router";

import MemberPersona from "@/entities/members/ui/memberPersona";
import { IProject, ProjectsTable } from "@/entities/projects";
import { ProjectAdd } from "@/features/projectAdd";
import { ProjectDelete } from "@/features/projectDelete";
import { FavoriteProject } from "@/features/projectToggleFavorite";
import { ROUTES } from "@/shared/config";
import {
  Button,
  DropdownMenu,
  IDropdownMenuItem,
  Layout,
  Link,
} from "@/shared/ui";

import styles from "./ProjectsPage.module.scss";

function ProjectsPage() {
  const { t } = useTranslation("pages.projectsPage");
  const navigate = useNavigate();
  const [currentProject, setCurrentProject] = React.useState({} as IProject);
  const [isOpenDelete, setIsOpenDelete] = React.useState(false);
  const [isOpenAdd, setIsOpenAdd] = React.useState(false);

  const rowActions = (project: IProject): IDropdownMenuItem[] => {
    return [
      {
        text: (
          <Link
            className={styles["project-page__link"]}
            href={ROUTES.projectSettings(project.id)}
          >
            {t("edit")}
          </Link>
        ),
      },
      {
        text: t("delete"),
        action: () => {
          setCurrentProject(project);
          setIsOpenDelete(true);
        },
        theme: "danger",
      },
    ];
  };

  const breadCrumbsItems = [
    {
      text: t("title"),
      link: ROUTES.projects,
    },
  ];

  const moveToProject = (project: IProject) => {
    navigate(ROUTES.project(project.id));
  };

  return (
    <Layout items={breadCrumbsItems}>
      <ProjectsTable
        favoriteProject={(isFavorite, projectId) => (
          <FavoriteProject isFavorite={isFavorite} projectId={projectId} />
        )}
        headerActions={
          <Button
            iconLeft={<Plus />}
            size="l"
            view="normal"
            onClick={() => setIsOpenAdd(true)}
          >
            {t("add-new-project")}
          </Button>
        }
        createdBy={(memberId) => (
          <div className={styles["project-page__creator"]}>
            <MemberPersona memberId={memberId} />
          </div>
        )}
        rowActions={(project) => <DropdownMenu items={rowActions(project)} />}
      />
      <ProjectAdd
        isOpen={isOpenAdd}
        onClose={() => setIsOpenAdd(false)}
        onSuccess={moveToProject}
      />
      <ProjectDelete
        project={currentProject}
        isOpen={isOpenDelete}
        onClose={() => setIsOpenDelete(false)}
      />
    </Layout>
  );
}

export default ProjectsPage;
