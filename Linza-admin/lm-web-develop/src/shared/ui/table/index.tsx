import React from "react";

import { Table as GTable } from "@gravity-ui/uikit";
import { useTranslation } from "react-i18next";

import { PAGE_SIZE } from "@/shared/config";

import Skeleton from "../skeleton";

interface ITable<T> {
  className?: string;
  data: T[];
  columns: {
    id: string;
    name: string;
    template: (item: T, index: number) => React.ReactNode;
  }[];
  pageSize?: number;
  isLoad: boolean;
  onRowClick?: (item: T) => void;
}

function Table<T extends { id: string }>({
  data,
  isLoad,
  columns,
  className,
  pageSize = PAGE_SIZE,
  onRowClick,
}: ITable<T>) {
  const { t } = useTranslation("shared.table");
  let tableData;
  if (isLoad) {
    tableData = Array.from({ length: pageSize }, () => ({})) as T[];
  } else {
    tableData = data;
  }

  const newColumns = columns.map((column) => {
    return {
      ...column,
      template: (item: T, index: number) => {
        if (isLoad) {
          return <Skeleton isLoad={isLoad} height={18} />;
        } else {
          return column.template(item, index);
        }
      },
    };
  });
  return (
    <GTable
      className={className}
      emptyMessage={t("emptyMessage")}
      data={tableData}
      columns={newColumns}
      onRowClick={onRowClick}
    />
  );
}

export default Table;
