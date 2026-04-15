import React from "react";

import { Label as GLabel } from "@gravity-ui/uikit";

interface ILabel {
  className?: string;
  theme?: "normal" | "info" | "warning" | "danger" | "success" | "unknown";
  size?: "m" | "s" | "xs";
  children: React.ReactNode;
}
function Label({ className, theme, children, size }: ILabel) {
  return (
    <GLabel className={className} theme={theme} size={size}>
      {children}
    </GLabel>
  );
}
Label.defaultProps = {
  theme: "normal",
  size: "xs",
};
export default Label;
