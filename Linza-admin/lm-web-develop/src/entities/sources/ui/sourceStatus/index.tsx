import { useTranslation } from "react-i18next";

import { SourceExecutionStatus } from "@/entities/sources/models/types";
import Label from "@/shared/ui/label";

interface IProps {
  executionStatus: SourceExecutionStatus;
}

function SourceStatusEntity({ executionStatus }: IProps) {
  const { t } = useTranslation("entities.sourceStatus");

  const sourceStatus = {
    planned: "unknown" as const,
    inprogress: "info" as const,
    notconfigure: "normal" as const,
    stopped: "normal" as const,
  };

  const sourceValue = {
    planned: "planned",
    inprogress: "in-progress",
    notconfigure: "not-configure",
    stopped: "stopped",
  };

  return (
    <Label theme={sourceStatus[executionStatus]}>
      {t(sourceValue[executionStatus])}
    </Label>
  );
}

export default SourceStatusEntity;
