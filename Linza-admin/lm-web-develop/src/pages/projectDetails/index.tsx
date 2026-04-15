import React from "react";

import { TrashBin } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router";

import { useProjectQuery } from "@/entities/projects";
import { ProjectChangeAvatar } from "@/features/projectChangeAvatar";
import { ProjectChangeName } from "@/features/projectChangeName";
import { ProjectDelete } from "@/features/projectDelete";
import { ProjectManagementMember } from "@/features/projectManagementMember";
import { ROUTES } from "@/shared/config";
import { Button, Layout } from "@/shared/ui";

import styles from "./ProjectDetails.module.scss";

function ProjectDetailsPage() {
  const { t } = useTranslation("pages.projectDetails");
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { project, isPending } = useProjectQuery(projectId!);

  const breadCrumbsItems = [
    {
      text: project.name,
      link: ROUTES.project(project.id),
      isPending: isPending,
    },
    {
      text: t("settings"),
      link: "",
    },
  ];

  return (
    <div className={styles["project-details-page"]}>
      <Layout items={breadCrumbsItems}>
        <div className={styles["project-details-page__header"]}>
          <div className={styles["project-details-page__wrapper"]}>
            <div className={styles["project-details-page__inputs"]}>
              <ProjectChangeAvatar project={project} />
              <ProjectChangeName project={project} />
            </div>
          </div>
          <div>
            <Button
              view="normal"
              size="l"
              onClick={() => setIsOpen(!isOpen)}
              iconLeft={<Icon data={TrashBin} size={16} />}
            >
              {t("delete")}
            </Button>
            <ProjectDelete
              project={project}
              isOpen={isOpen}
              onClose={() => setIsOpen(false)}
              onSuccess={() => navigate(ROUTES.projects)}
            />
          </div>
        </div>
        <ProjectManagementMember projectId={project.id} />
      </Layout>
    </div>
  );
}

export default ProjectDetailsPage;
