import React from "react";

import { Navigate } from "react-router";
import { Outlet } from "react-router-dom";

import { useAuth } from "@/entities/session";
import TriggerSwitcherNotAuth from "@/features/language/ui/triggerSwitcherNotAuth";
import { ROUTES } from "@/shared/config";

function GuestProvider() {
  const isAuth = useAuth();

  if (isAuth) {
    return <Navigate to={ROUTES.dashboard} />;
  }

  return (
    <>
      <TriggerSwitcherNotAuth />
      <Outlet />
    </>
  );
}

export default GuestProvider;
