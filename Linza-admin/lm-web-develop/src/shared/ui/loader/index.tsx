import { Loader as GLoader } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Loader.module.scss";

function Loader({
  className,
  size,
}: {
  className?: string;
  size?: "s" | "m" | "l";
}) {
  const classes = cn(className, styles.loader);
  return <GLoader className={classes} size={size} />;
}

Loader.defaultProps = {
  size: "m",
};
export default Loader;
