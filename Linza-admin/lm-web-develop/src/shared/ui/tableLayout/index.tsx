import { ReactElement, ReactNode } from "react";

import cn from "classnames";

import styles from "./TableLayout.module.scss";

function TableLayout({
  className,
  children,
}: {
  className?: string;
  children: [
    ReactElement<typeof Header>,
    ReactElement<typeof Body>,
    ReactElement<typeof Footer>,
  ];
}) {
  const classes = cn(styles["table-layout"], className);
  return (
    <div className={classes}>
      <div className={styles["table-layout__header"]}>{children[0]}</div>
      <div className={styles["table-layout__body"]}>{children[1]}</div>
      <div className={styles["table-layout__footer"]}>{children[2]}</div>
    </div>
  );
}

function Header({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
function Body({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
function Footer({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

TableLayout.Header = Header;
TableLayout.Body = Body;
TableLayout.Footer = Footer;

export default TableLayout;
