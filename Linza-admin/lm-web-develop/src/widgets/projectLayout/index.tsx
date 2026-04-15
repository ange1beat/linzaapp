import React, { ReactNode } from "react";

import {
  ChartMixed,
  Code,
  Files,
  FileText,
  Folder,
  Gear,
} from "@gravity-ui/icons";
import { Icon, Tabs } from "@gravity-ui/uikit";
import cn from "classnames";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { useFoldersQuery } from "@/entities/folders/api/queries";
import { useGetProjectMembersQuery } from "@/entities/members/api/queries";
import { useProjectQuery } from "@/entities/projects";
import { ROUTES } from "@/shared/config";
import { Button, Layout } from "@/shared/ui";

import styles from "./ProjectLayout.module.scss";

function ProjectLayout({
  children,
  projectId,
  currentTab,
  classNames,
}: {
  children: ReactNode;
  projectId: string;
  currentTab:
    | "dashboard"
    | "folders"
    | "reports"
    | "documents"
    | "sources"
    | "members";
  classNames?: string;
}) {
  const { t } = useTranslation("widgets.projectLayout");
  const classes = cn(styles["project-layout"], classNames);
  const { project, isPending } = useProjectQuery(projectId!);
  const membersInProject = useGetProjectMembersQuery(projectId);
  const folders = useFoldersQuery(projectId);

  const breadCrumbs = [
    {
      text: project.name,
      link: "",
      isPending: isPending,
    },
  ];
  const emptyFn = () => {};

  return (
    <Layout
      items={breadCrumbs}
      actions={
        <Link to={ROUTES.projectSettings(projectId)}>
          <Button
            view="normal"
            size="s"
            iconLeft={<Icon data={Gear} size={16} />}
          >
            {t("settings")}
          </Button>
        </Link>
      }
      menu={
        <Tabs activeTab={currentTab} size="xl" className={classes}>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.project(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              icon={<Icon data={ChartMixed} size={16} />}
              id="dashboard"
              title={t("dashboard")}
              onClick={emptyFn}
            />
          </Link>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.folders(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              icon={<Icon data={Folder} size={16} />}
              id="folders"
              title={t("folders")}
              counter={folders.total}
              onClick={emptyFn}
            />
          </Link>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.reports(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              icon={<Icon data={FileText} size={16} />}
              id="reports"
              title={t("reports")}
              // counter={5}  TODO: Add total for reports
              onClick={emptyFn}
            />
          </Link>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.documents(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              icon={<Icon data={Files} size={16} />}
              id="documents"
              title={t("documents")}
              // counter={2} TODO: Add total for documents
              onClick={emptyFn}
            />
          </Link>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.sources(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              id="sources"
              title={t("sources")}
              // counter={9} TODO: Add total for sources
              onClick={emptyFn}
            />
          </Link>
          <Link
            className={styles["project-layout__link"]}
            to={ROUTES.projectMembers(projectId)}
          >
            <Tabs.Item
              className={styles["project-layout__tab"]}
              icon={<Icon data={Code} size={16} />}
              id="members"
              title={t("members")}
              counter={membersInProject.total}
              onClick={emptyFn}
            />
          </Link>
        </Tabs>
      }
    >
      {children}
    </Layout>
  );
}

export default ProjectLayout;
