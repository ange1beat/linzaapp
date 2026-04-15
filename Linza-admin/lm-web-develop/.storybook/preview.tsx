import React from "react";

import { ThemeProvider } from "@gravity-ui/uikit";
import "@gravity-ui/uikit/styles/fonts.css";
import "@gravity-ui/uikit/styles/styles.css";
import type { Preview } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router";

import "@/app/i18n";
import { AlertProvider } from "@/shared/ui";

import "../src/app/App.module.scss";
import "../src/app/theme.scss";

const queryClient = new QueryClient();

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    mockAddonConfigs: {
      globalMockData: [],
      ignoreQueryParams: true,
      disableUsingOriginal: false,
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider theme="light">
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={["/?invitationId=123412341"]}>
            <AlertProvider>
              <Story />
            </AlertProvider>
          </MemoryRouter>
        </QueryClientProvider>
      </ThemeProvider>
    ),
  ],
};

export default preview;
