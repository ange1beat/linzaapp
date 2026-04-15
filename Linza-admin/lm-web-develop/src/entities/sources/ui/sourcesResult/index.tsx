import { useTranslation } from "react-i18next";

import { SourceLastResult } from "@/entities/sources/models/types";
import Label from "@/shared/ui/label";

interface IProps {
  status?: SourceLastResult;
}

function SourcesResultEntity({ status }: IProps) {
  const { t } = useTranslation("entities.sourcesResult");
  const statusTheme = {
    success: "success" as const,
    error: "danger" as const,
  };

  return status && <Label theme={statusTheme[status]}>{t(status)}</Label>;
}

export default SourcesResultEntity;
