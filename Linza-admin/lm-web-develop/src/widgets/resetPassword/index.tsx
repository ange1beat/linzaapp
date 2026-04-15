import React from "react";

import cn from "classnames";
import { useNavigate } from "react-router";

import { LoginType } from "@/entities/auth";
import {
  VerifyOTP,
  LoginInput,
  OTPReRequest,
  SetPassword,
} from "@/features/pwdRecovery";
import { ROUTES } from "@/shared/config";

import styles from "./ResetPasswordWidget.module.scss";

function ResetPasswordWidget({ className }: { className?: string }) {
  const [step, setStep] = React.useState<1 | 2 | 3>(1);
  const [token, setToken] = React.useState<string>("");
  const [login, setLogin] = React.useState("");
  const [loginType, setLoginType] = React.useState<LoginType>();
  const navigate = useNavigate();

  const sendCodeHandler = (lgn: string, type: LoginType) => {
    setLogin(lgn);
    setLoginType(type);
    setStep(2);
  };

  const confirmCodeHandler = (stateToken: string) => {
    setStep(3);
    setToken(stateToken);
  };

  const resetPasswordHandler = () => {
    navigate(ROUTES.resetPasswordSuccess);
  };

  const onBack = () => {
    setStep(1);
  };
  const classes = cn(className, styles["reset-password-widget"]);
  return (
    <div className={classes}>
      {step === 1 && <LoginInput onSuccess={sendCodeHandler} />}
      {step === 2 && loginType && (
        <VerifyOTP
          onSuccess={confirmCodeHandler}
          login={login}
          loginType={loginType}
          onBack={onBack}
        >
          <OTPReRequest login={login} loginType={loginType} />
        </VerifyOTP>
      )}
      {step === 3 && token && (
        <SetPassword recoveryToken={token} onSuccess={resetPasswordHandler} />
      )}
    </div>
  );
}

export default ResetPasswordWidget;
