import React from "react";

import { ChevronUp } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import cn from "classnames";

import Button from "../button";

import styles from "./Accordion.module.scss";

interface AccordionHeadProps {
  children: React.ReactNode;
}
interface AccordionBodyProps {
  children: React.ReactNode;
}
interface AccordionProps {
  className?: string;
  children: [
    React.ReactElement<typeof AccordionHead>,
    React.ReactElement<typeof AccordionBody>,
  ];
}

function Accordion({ className, children }: AccordionProps) {
  const [open, setOpen] = React.useState(false);
  const onToggleHandler = () => {
    setOpen((prevState) => !prevState);
  };

  const classes = cn(styles.accordion, className);
  const classesIcon = cn(styles["accordion__icon"], {
    [styles["--active"]]: open,
  });
  const classesBody = cn(styles["accordion__body"], {
    [styles["--visible"]]: open,
  });
  return (
    <div className={classes}>
      <div className={styles["accordion__head"]}>
        {children[0]}
        <Button size="xs" view="normal" onClick={onToggleHandler}>
          <Icon data={ChevronUp} className={classesIcon} />
        </Button>
      </div>
      <div className={classesBody}>{children[1]}</div>
    </div>
  );
}

function AccordionBody({ children }: AccordionBodyProps) {
  return <>{children}</>;
}

function AccordionHead({ children }: AccordionHeadProps) {
  return <>{children}</>;
}

Accordion.Head = AccordionHead;
Accordion.Body = AccordionBody;

export default Accordion;
