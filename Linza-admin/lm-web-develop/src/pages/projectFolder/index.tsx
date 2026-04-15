import React from "react";

import { useParams } from "react-router";
import { Link } from "react-router-dom";

import { ROUTES } from "@/shared/config";

function ProjectFolderPage() {
  const { projectId, folderId } = useParams();
  return <Link to={ROUTES.folder(projectId!, folderId!)}>Folder</Link>;
}

export default ProjectFolderPage;
