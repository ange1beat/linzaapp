import React from "react";

import { Check } from "@gravity-ui/icons";
import { Icon, List as GList } from "@gravity-ui/uikit";
import cn from "classnames";
import isEmpty from "lodash/isEmpty";

import { PAGE_SIZE } from "@/shared/config";

import Skeleton from "../skeleton";

import styles from "./List.module.scss";

interface IListProps<T extends { id: string }> {
  placeholder: string;
  emptyMessage: string;
  items: T[];
  renderItem: (
    item: T,
    isSelected: boolean,
    isDisabled: boolean,
    index: number,
  ) => React.ReactNode;
  onSearch?: (value: string) => void;
  isLoad: boolean;
  isSelected: (item: T) => boolean;
  isDisabled: (item: T) => boolean;
  onToggleSelect: (id: string) => void;
  itemHeight: number;
  listHeight: number;
  filterValue?: string;
  view?: "outline" | "default";
  disabled?: boolean;
  className?: string;
}

function List<T extends { id: string }>({
  placeholder,
  emptyMessage,
  isLoad,
  items,
  renderItem,
  onToggleSelect,
  onSearch,
  isSelected,
  isDisabled,
  itemHeight,
  listHeight,
  filterValue,
  view,
  className,
}: IListProps<T>) {
  let itemsList = Array.from({ length: PAGE_SIZE }, () => ({}) as T);

  const classes = cn(styles.list, {
    [styles["list--outline"]]: view === "outline",
    [styles["list--empty"]]: items.length === 0,
  });
  const classesFilter = cn(styles["list__filter"], {
    [styles["list__filter--outline"]]: view === "outline",
  });

  const renderItemHandler = (
    item: T & { disabled?: boolean },
    _: boolean,
    itemIndex: number,
  ) => {
    if (isLoad || isEmpty(item)) {
      return (
        <Skeleton
          isLoad={isLoad}
          height={itemHeight}
          className={styles["list__skeleton"]}
        />
      );
    }

    const selectedItem = isSelected(item);
    const disabledItem = item.disabled || false;
    const classesIcon = cn(styles["list__check-icon"], {
      [styles["list__check-icon--visible"]]: selectedItem,
      [styles["list__check-icon--invisible"]]: !selectedItem,
    });
    const classesItem = cn(styles["list__item"], {
      [styles["list__item--disabled"]]: disabledItem,
    });
    return (
      <div className={classesItem}>
        <Icon data={Check} className={classesIcon} />
        {renderItem(item, selectedItem, disabledItem, itemIndex)}
      </div>
    );
  };

  if (!isLoad) {
    itemsList = items.map((item) => ({
      disabled: isDisabled(item),
      ...item,
    }));
  }

  return (
    <GList
      filterPlaceholder={placeholder}
      emptyPlaceholder={emptyMessage}
      renderItem={renderItemHandler}
      items={itemsList}
      onItemClick={(list) => onToggleSelect(list.id)}
      onFilterUpdate={onSearch}
      itemHeight={itemHeight}
      itemsHeight={listHeight}
      itemClassName={styles["list__row"]}
      filterClassName={classesFilter}
      itemsClassName={classes}
      filter={filterValue}
      virtualized={false}
      className={className}
    />
  );
}

List.defaultProps = {
  isSelected: () => false,
  isDisabled: () => false,
};

export default List;
