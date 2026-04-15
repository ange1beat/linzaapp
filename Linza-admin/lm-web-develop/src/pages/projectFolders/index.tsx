import React from "react";

import { FolderPlus } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router";

import { FoldersList, IFolder } from "@/entities/folders";
import { FolderDelete } from "@/features/folderDelete";
import { Button } from "@/shared/ui";
import ProjectLayout from "@/widgets/projectLayout";

function ProjectFolders() {
  const { t } = useTranslation("pages.projectFolders");
  const { projectId } = useParams();
  const [currentFolder, setCurrentFolder] = React.useState<IFolder>({
    id: "",
    name: "",
  });
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  return (
    <ProjectLayout currentTab="folders" projectId={projectId!}>
      <FolderDelete
        folder={currentFolder}
        isOpen={isOpen}
        projectId={projectId!}
        onCancel={() => setIsOpen(false)}
      />
      <FoldersList
        addAction={
          <Button
            view="normal"
            size="l"
            iconLeft={<Icon data={FolderPlus} size={16} />}
            href="" // TODO: add link
          >
            {t("add-folder")}
          </Button>
        }
        deleteAction={(folder) => {
          setIsOpen(true);
          setCurrentFolder(folder);
        }}
        projectId={projectId!}
      />
    </ProjectLayout>
  );
}

export default ProjectFolders;
