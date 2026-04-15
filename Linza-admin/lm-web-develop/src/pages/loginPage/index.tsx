import React from "react";

import { redirect } from "react-router-dom";

import type { LoginType } from "@/entities/auth";
import { addToken, IUserLogin } from "@/entities/session";
import { LoginFeature } from "@/features/auth";
import { useGetAuthToken } from "@/features/auth/api/queries";
import { ROUTES } from "@/shared/config";

import AuthTwoFA from "../../widgets/authTwoFA";

import styles from "./LoginPage.module.scss";

function LoginPage() {
  const [step, setStep] = React.useState<1 | 2>(1);
  const [loginType, setLoginType] = React.useState<LoginType>("email");
  const [stateToken, setStateToken] = React.useState<string>("");
  const [user, setUser] = React.useState<IUserLogin>();
  const useGetAuthTokenMutation = useGetAuthToken();

  function onSuccessHandler(u: IUserLogin, token: string, lType: LoginType) {
    setStep(2);
    setStateToken(token);
    setLoginType(lType);
    setUser(u);
  }

  function onBackHandler() {
    setStep(1);
  }

  function onLoginHandler(u: IUserLogin, token: string) {
    useGetAuthTokenMutation
      .mutateAsync(token)
      .then((data) => {
        addToken(data.accessToken);
        redirect(ROUTES.dashboard);
      })
      .catch();
  }

  return (
    <div className={styles["login-page"]}>
      {step === 1 && <LoginFeature onSuccess={onSuccessHandler} />}
      {step === 2 && user && (
        <AuthTwoFA
          isLoading={useGetAuthTokenMutation.isPending}
          loginType={loginType}
          stateToken={stateToken}
          onSuccess={onLoginHandler}
          onError={() => {}}
          onBack={onBackHandler}
        />
      )}
    </div>
  );
}

export default LoginPage;
