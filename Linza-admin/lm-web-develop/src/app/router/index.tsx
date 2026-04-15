import React from "react";

import { RouterProvider } from "react-router-dom";

import publicRoutes from "./routes";

function Router() {
  return <RouterProvider router={publicRoutes} />;
}

export default Router;
