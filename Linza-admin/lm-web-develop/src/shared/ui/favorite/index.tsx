import { Star, StarFill } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Favorite.module.scss";

function Favorite({
  className,
  isSelected,
  onClick,
}: {
  className?: string;
  isSelected: boolean;
  onClick?: () => void;
}) {
  const classes = cn(className, styles.favorite, {
    [styles["favorite--selected"]]: isSelected,
  });
  const icon = isSelected ? StarFill : Star;
  return (
    <div className={classes} onClick={onClick}>
      <Icon data={icon} />
    </div>
  );
}
export default Favorite;
