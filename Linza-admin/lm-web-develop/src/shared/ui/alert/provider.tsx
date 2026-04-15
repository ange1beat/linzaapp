import React from "react";

import AlertContainer from "./container";
import { IAlert, IAlertContext, IAlertOptions } from "./types";

const AlertContext = React.createContext<IAlertContext>({
  addAlert: () => null,
  delAlert: () => null,
});

let id = 1;

const AlertProvider = ({ children }: { children: React.ReactNode }) => {
  const [alerts, setAlerts] = React.useState<IAlert[]>([]);

  const addAlert = React.useCallback(
    (alert: IAlertOptions) => {
      setAlerts((prevAlert) => [...prevAlert, { id: id++, options: alert }]);
    },
    [setAlerts],
  );

  const delAlert = React.useCallback(
    (alertId: number) => {
      setAlerts((toasts) => toasts.filter((t) => t.id !== alertId));
    },
    [setAlerts],
  );

  return (
    <AlertContext.Provider value={{ addAlert, delAlert }}>
      <AlertContainer alerts={alerts} />
      {children}
    </AlertContext.Provider>
  );
};

const useAlert = () => {
  return React.useContext(AlertContext);
};

export { AlertProvider, AlertContext, useAlert };
