import { Spin as GSpin } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Spin.module.scss";

function Spin({
  className,
  size,
}: {
  className?: string;
  size: "xs" | "s" | "m" | "l" | "xl";
}) {
  const classes = cn(className, styles.spin);
  return <GSpin className={classes} size={size} />;
}

export default Spin;
