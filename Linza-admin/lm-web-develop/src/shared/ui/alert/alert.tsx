import React from "react";

import { Alert as GAlert } from "@gravity-ui/uikit";

import { useAlert } from "./provider";
import { IAlert } from "./types";

const AUTO_HIDING = 5000;

function Alert(props: IAlert, ref: React.ForwardedRef<HTMLDivElement>) {
  const { id, options } = props;
  const { delAlert } = useAlert();

  React.useEffect(() => {
    const timer = setTimeout(() => {
      delAlert(id);
    }, AUTO_HIDING);

    return () => {
      clearTimeout(timer);
    };
  }, [id, delAlert]);

  return (
    <div ref={ref}>
      <GAlert
        title={options.title}
        message={options.message}
        theme={options.theme}
        layout="horizontal"
        onClose={() => delAlert(id)}
      />
    </div>
  );
}

export default React.forwardRef(Alert);
