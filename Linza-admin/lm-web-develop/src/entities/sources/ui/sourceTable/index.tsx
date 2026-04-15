import React from "react";

import { Magnifier } from "@gravity-ui/icons";
import { useTranslation } from "react-i18next";

import { useGetSourcesQuery } from "@/entities/sources/api/queries";
import {
  ISource,
  SourceExecutionStatus,
  SourceLastResult,
  SourceType,
} from "@/entities/sources/models/types";
import {
  SourcesResultEntity,
  SourceStatusEntity,
  SourcesTypeEntity,
} from "@/entities/sources/ui";
import { PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/shared/config";
import { useDebounce } from "@/shared/hooks";
import {
  Filter,
  Input,
  Link,
  Pagination,
  Table,
  TableLayout,
  Text,
} from "@/shared/ui";

import styles from "./SourceTableEntity.module.scss";

interface IProps {
  statusControl: (source: ISource) => React.ReactNode;
  actions: (source: ISource) => React.ReactNode;
  headerActions: React.ReactNode;
}

function SourceTableEntity({ statusControl, actions, headerActions }: IProps) {
  const { t } = useTranslation("entities.sourceTable");
  const [pageNumber, setPageNumber] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(PAGE_SIZE);
  const [searchStr, setSearchStr, debouncedStr] = useDebounce<string>("");
  const [filterValues, setFilterValues] = React.useState<{
    [k: string]: string[];
  }>({});

  const onChangeFilter = (value: { [p: string]: string[] }) => {
    setFilterValues(value);
  };

  const sourcesQuery = useGetSourcesQuery({
    search: debouncedStr,
    pageSize,
    pageNumber,
    filterValues,
  });

  const paginationUpdateHandler = (p: number, pSize: number) => {
    setPageNumber(p);
    setPageSize(pSize);
  };

  const groups = [
    {
      label: t("execution-status"),
      name: "executionStatus",
      options: [
        { value: SourceExecutionStatus.Planned, label: t("statuses.planned") },
        { value: SourceExecutionStatus.Stopped, label: t("statuses.stopped") },
        {
          value: SourceExecutionStatus.NotConfigure,
          label: t("statuses.not-configure"),
        },
        {
          value: SourceExecutionStatus.InProgress,
          label: t("statuses.in-progress"),
        },
      ],
    },
    {
      label: t("last-result"),
      name: "lastResult",
      options: [
        { value: SourceLastResult.Success, label: t("results.success") },
        { value: SourceLastResult.Error, label: t("results.error") },
      ],
    },
    {
      label: t("type-source"),
      name: "typeSource",
      options: [
        { value: SourceType.Telegram, label: t("sources.telegram") },
        { value: SourceType.Web, label: t("sources.web") },
        { value: SourceType.VK, label: t("sources.vk") },
        { value: SourceType.OK, label: t("sources.ok") },
      ],
    },
  ];

  const columns = [
    {
      id: "type",
      name: t("columns.type"),
      template: (source: ISource) => <SourcesTypeEntity type={source.type} />,
    },
    {
      id: "url",
      name: t("columns.url"),
      template: (source: ISource) => (
        <Link href={source.url} target="_blank">
          {source.url}
        </Link>
      ),
    },
    {
      id: "statusControl",
      name: "",
      template: (source: ISource) => statusControl(source),
    },
    {
      id: "nextLaunch",
      name: t("columns.next-launch"),
      template: (source: ISource) => (
        <Text variant="body-1">
          {t("time", {
            hours: Math.floor(source.nextLaunch / 3600),
            minutes: Math.floor(source.nextLaunch / 3600 / 60),
          })}
        </Text>
      ),
    },
    {
      id: "executionStatus",
      name: t("columns.execution-status"),
      template: (source: ISource) => (
        <SourceStatusEntity executionStatus={source.executionStatus} />
      ),
    },
    {
      id: "lastResult",
      name: t("columns.last-result"),
      template: (source: ISource) => (
        <SourcesResultEntity status={source.lastResult} />
      ),
    },
    {
      id: "actions",
      name: "",
      template: (source: ISource) => actions(source),
    },
  ];

  return (
    <TableLayout>
      <TableLayout.Header>
        <div className={styles["source-table__header"]}>
          <div className={styles["source-table__actions"]}>
            <Input
              value={searchStr}
              onChange={setSearchStr}
              size="l"
              placeholder={t("search-placeholder")}
              rightContent={
                <Magnifier className={styles["source-table__icon"]} />
              }
            />
            <Filter
              groups={groups}
              value={filterValues}
              onChange={onChangeFilter}
            />
            {headerActions}
          </div>
        </div>
      </TableLayout.Header>
      <TableLayout.Body>
        <Table
          className={styles["source-table__table"]}
          columns={columns}
          data={sourcesQuery.sources}
          isLoad={sourcesQuery.isPending}
        />
      </TableLayout.Body>
      <TableLayout.Footer>
        <Pagination
          total={sourcesQuery.total}
          page={pageNumber}
          pageSize={pageSize}
          pageSizeOptions={PAGE_SIZE_OPTIONS}
          onUpdate={paginationUpdateHandler}
        />
      </TableLayout.Footer>
    </TableLayout>
  );
}

export default SourceTableEntity;
