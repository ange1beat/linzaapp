import React, { useEffect } from "react";

import cn from "classnames";
import { useTranslation } from "react-i18next";

import { Button } from "@/shared/ui";

import Text from "../text";

import secondsConverter from "./secondsConverter";

import styles from "./Timer.module.scss";

interface ITimerProps {
  className?: string;
  isLoading: boolean;
  timer: number;
  template?: (timerValue: string) => string;
  countDownEndText?: string;
  actions: () => void;
  tabIndex?: number;
}

function Timer(props: ITimerProps) {
  const { t } = useTranslation("shared.timer");
  const [timer, setTimer] = React.useState(props.timer);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (timer > 0) {
      timeoutId = setTimeout(() => {
        setTimer((prevTimer) => prevTimer - 1);
      }, 1000);
    }

    return () => {
      clearTimeout(timeoutId);
    };
  }, [timer]);

  const resetTimer = () => {
    setTimer(props.timer);
    props.actions();
  };

  let template;
  if (props.template) {
    template = props.template;
  } else {
    template = (time: string) => t("request-wait", { timer: time });
  }

  let countDownEndText;
  if (props.countDownEndText) {
    countDownEndText = props.countDownEndText;
  } else {
    countDownEndText = t("request-again");
  }

  const classes = cn(styles["main-timer"], props.className);
  return (
    <Button
      view="outlined"
      disabled={timer !== 0}
      className={classes}
      size="xl"
      width="max"
      onClick={resetTimer}
      loading={props.isLoading}
      tabIndex={props.tabIndex}
    >
      <Text variant="body-2">
        {timer > 0 && template(secondsConverter(timer).toString())}
        {timer === 0 && countDownEndText}
      </Text>
    </Button>
  );
}

export default Timer;
