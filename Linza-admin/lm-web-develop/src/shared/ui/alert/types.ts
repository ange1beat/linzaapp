import React from "react";

export type IAlert = {
  id: number;
  options: IAlertOptions;
};

export type IAlertOptions = {
  title: string;
  theme: "success" | "warning" | "danger";
  message: React.ReactNode;
};

export type IAlertContext = {
  addAlert: (a: IAlertOptions) => void;
  delAlert: (id: number) => void;
};
