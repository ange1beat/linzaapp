import React from "react";

import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router";

import "./mocks";

function ProvidersWrapper({ children }: { children: React.ReactNode }) {
  return <MemoryRouter initialEntries={["/"]}>{children}</MemoryRouter>;
}

function customRender(component: JSX.Element) {
  const { baseElement } = render(component, { wrapper: ProvidersWrapper });
  return baseElement;
}

export { customRender as render };
