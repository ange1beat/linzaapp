import React from "react";

import { Pagination as GPagination } from "@gravity-ui/uikit";
import cn from "classnames";

import styles from "./Pagination.module.scss";

interface IPagination {
  className?: string;
  total: number;
  page: number;
  pageSize: number;
  pageSizeOptions: number[];
  onUpdate: (page: number, pageSize: number) => void;
}
function Pagination({
  className,
  page,
  pageSize,
  pageSizeOptions,
  total,
  onUpdate,
}: IPagination) {
  const classes = cn(styles.pagination, className);
  return (
    <GPagination
      className={classes}
      page={page}
      pageSize={pageSize}
      showInput={true}
      pageSizeOptions={pageSizeOptions}
      total={total}
      onUpdate={onUpdate}
    />
  );
}

export default Pagination;
