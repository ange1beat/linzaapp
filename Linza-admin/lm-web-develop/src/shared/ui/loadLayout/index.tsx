import React from "react";

import Loader from "../loader";

import styles from "./LoadLayout.module.scss";

interface ILoadLayout {
  isLoad: boolean;
  children: React.ReactNode;
  size?: "s" | "m" | "l";
}

function LoadLayout({ isLoad, children, size }: ILoadLayout) {
  return (
    <>
      {isLoad ? (
        <Loader size={size} className={styles["load-layout"]} />
      ) : (
        children
      )}
    </>
  );
}
LoadLayout.defaultProps = {
  size: "l",
};

export default LoadLayout;
