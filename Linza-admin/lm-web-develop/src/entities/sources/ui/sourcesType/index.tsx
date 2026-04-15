import {
  OKIcon,
  TelegramIcon,
  VKIcon,
  WebIcon,
} from "@/entities/sources/media";
import { SourceType } from "@/entities/sources/models/types";

import styles from "./SourceTypeEntity.module.scss";

interface IProps {
  type: SourceType;
}

function SourcesTypeEntity({ type }: IProps) {
  const sourceIcon = {
    web: <WebIcon />,
    vk: <VKIcon />,
    telegram: <TelegramIcon />,
    ok: <OKIcon />,
  };

  return <div className={styles["source-icon"]}>{sourceIcon[type]}</div>;
}

export default SourcesTypeEntity;
