import React from "react";

import { useParams } from "react-router";

import ProjectLayout from "@/widgets/projectLayout";

function ProjectDashboardPage() {
  const { projectId } = useParams();

  return (
    <ProjectLayout projectId={projectId!} currentTab="dashboard">
      Dashboard
    </ProjectLayout>
  );
}

export default ProjectDashboardPage;
