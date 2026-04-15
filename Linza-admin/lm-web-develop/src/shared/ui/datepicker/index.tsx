import React, { SyntheticEvent } from "react";

import { Calendar } from "@gravity-ui/icons";
import { Icon } from "@gravity-ui/uikit";
import cn from "classnames";
import { addMonths, isEqual, isWithinInterval, Locale } from "date-fns";
import { enGB, ru } from "date-fns/locale";
import i18n from "i18next";
import ReactDatePicker, { CalendarContainerProps } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useTranslation } from "react-i18next";

import { Button } from "@/shared/ui";

import styles from "./Datepicker.module.scss";

interface IDate {
  startDate: Date | null;
  endDate: Date | null;
}

function CalendarContainer({
  clearHandler,
  onClick,
  props,
  disabled,
}: {
  clearHandler: () => void;
  onClick: () => void;
  disabled: boolean;
  props: CalendarContainerProps;
}) {
  const { t } = useTranslation("controls");
  return (
    <div className={styles["datepicker__wrapper"]}>
      <div className={styles["datepicker__content"]}>
        {props.children}
        <div className={styles["datepicker__buttons"]}>
          <Button view="normal" size="m" onClick={clearHandler}>
            {t("cancel")}
          </Button>
          <Button view="action" size="m" disabled={disabled} onClick={onClick}>
            {t("apply")}
          </Button>
        </div>
      </div>
    </div>
  );
}

function renderRangeDays(
  currentDay: Date,
  selectedDate: { startDate: Date | null; endDate: Date | null },
) {
  const isStartDate =
    selectedDate.startDate && isEqual(currentDay, selectedDate.startDate);
  const isEndDate =
    selectedDate.endDate && isEqual(currentDay, selectedDate.endDate);
  const isBetweenDates =
    selectedDate.startDate &&
    selectedDate.endDate &&
    isWithinInterval(currentDay, {
      start: selectedDate.startDate,
      end: selectedDate.endDate,
    });
  return cn(styles["datepicker__day"], {
    [styles["_first-day"]]: isStartDate,
    [styles["_last-day"]]: isEndDate,
    [styles["_between-days"]]: isBetweenDates,
  });
}

function CalendarIcon({
  onClick,
  open,
}: {
  onClick: () => void;
  open: boolean;
}) {
  const classes = cn(styles["datepicker__icon-wrapper"], {
    ["react-datepicker-ignore-onclickoutside"]: open,
  });
  return (
    <div className={classes} onClick={onClick}>
      <Icon data={Calendar} size={16} />
    </div>
  );
}

function Datepicker({
  value,
  onChange,
}: {
  value: IDate;
  onChange: (
    date: [Date, Date],
    event?: SyntheticEvent<never, Event> | undefined,
  ) => void;
}) {
  const [selectedDate, setSelectedDate] = React.useState(value);
  const { t } = useTranslation("shared.datepicker");
  const [open, setOpen] = React.useState(false);
  const clearHandler = () => {
    setSelectedDate({ startDate: null, endDate: null });
    setOpen(false);
  };

  const onChangeHandle = (rangeDate: [Date | null, Date | null]) => {
    const [start, end] = rangeDate;
    setSelectedDate({ startDate: start, endDate: end });
  };

  const onToggle = () => setOpen(!open);

  const currentLocale: Record<string, Locale> = {
    ru: ru,
    en: enGB,
  };

  return (
    <ReactDatePicker
      open={open}
      onClickOutside={clearHandler}
      onInputClick={onToggle}
      dateFormat="dd.MM.yyyy"
      selected={selectedDate.startDate}
      onChange={onChangeHandle}
      startDate={selectedDate.startDate}
      endDate={selectedDate.endDate}
      selectsRange
      locale={currentLocale[i18n.language] ?? "enGB"}
      maxDate={addMonths(new Date(), 0)}
      showDisabledMonthNavigation
      renderDayContents={(day) => <span>{day}</span>}
      formatWeekDay={(dayName) => t(dayName.toLowerCase())}
      calendarStartDay={1}
      showIcon
      isClearable
      toggleCalendarOnIconClick
      popperPlacement="bottom-end"
      icon={<CalendarIcon onClick={onToggle} open={open} />}
      calendarIconClassname={styles["datepicker__icon"]}
      clearButtonClassName={styles["datepicker__clear-icon"]}
      dayClassName={(day) => renderRangeDays(day, selectedDate)}
      placeholderText={t("placeholder")}
      calendarContainer={(props) => (
        <CalendarContainer
          props={props}
          clearHandler={clearHandler}
          onClick={() => {
            onChange([selectedDate.startDate!, selectedDate.endDate!]);
            setOpen(false);
          }}
          disabled={!selectedDate.endDate || !selectedDate.startDate}
        />
      )}
    />
  );
}

export default Datepicker;
