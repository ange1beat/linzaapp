import React from "react";

import { Portal } from "@gravity-ui/uikit";
import { animated, useTransition } from "@react-spring/web";

import Alert from "./alert";
import { IAlert } from "./types";

import styles from "./Alert.module.scss";

function AlertContainer({ alerts }: { alerts: IAlert[] }) {
  const refMap = React.useMemo(() => new WeakMap(), []);

  const transitions = useTransition(alerts, {
    from: { opacity: 0, height: 0, life: "100%" },
    enter: (item) => async (next) => {
      await next({ opacity: 1, height: refMap.get(item).offsetHeight });
    },
    leave: [{ opacity: 0 }, { height: 0 }],
    config: { tension: 125, friction: 20, precision: 0.1 },
  });

  return (
    <Portal>
      <div className={styles["alert-container"]}>
        {transitions(({ life, ...style }, item) => (
          <animated.div
            className={styles["alert-container__alert"]}
            style={style}
          >
            <Alert
              key={item.id}
              id={item.id}
              options={item.options}
              ref={(ref: HTMLDivElement) => ref && refMap.set(item, ref)}
            />
          </animated.div>
        ))}
      </div>
    </Portal>
  );
}

export default AlertContainer;
