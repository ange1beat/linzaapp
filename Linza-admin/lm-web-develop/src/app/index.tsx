import React from "react";

import { ThemeProvider } from "@gravity-ui/uikit";
import "@gravity-ui/uikit/styles/styles.css";
import { QueryClientProvider } from "@tanstack/react-query";

import { queryClient } from "@/shared/api";
import { AlertProvider } from "@/shared/ui";

import "../entities/session";

import "./i18n";
import Router from "./router";
import "./theme.scss";

import "./App.module.scss";

function App() {
  return (
    <ThemeProvider theme="light">
      <QueryClientProvider client={queryClient}>
        <AlertProvider>
          <Router />
        </AlertProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
