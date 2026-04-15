import React from "react";

import { Navigate, useLocation } from "react-router";

import { useAuth } from "../../entities/session";
import { ROUTES } from "../../shared/config/routes";

function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  const location = useLocation();
  const isAuth = useAuth();

  if (!isAuth) {
    return <Navigate to={ROUTES.login} state={{ from: location }} />;
  }

  return <>{children}</>;
}

export default AuthProvider;
