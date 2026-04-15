import React from "react";

import { useNavigate } from "react-router";
import { useSearchParams } from "react-router-dom";

import {
  RegistrationForm,
  useInvitationIdQuery,
} from "@/features/registration";
import { ROUTES } from "@/shared/config";
import { LoadLayout } from "@/shared/ui";

import styles from "./RegistrationPage.module.scss";

function RegistrationPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const invitationId = searchParams.get("invitationId");
  const { isPending, isError } = useInvitationIdQuery(invitationId || "");

  React.useEffect(() => {
    if (!invitationId || isError) {
      navigate(ROUTES.registrationError, { replace: true });
    }
  }, [invitationId, isError]);

  const onSuccessHandler = () => {
    navigate(ROUTES.registrationSuccess, { replace: true });
  };

  return (
    <div className={styles["registration-page"]}>
      <LoadLayout isLoad={isPending}>
        {invitationId && (
          <RegistrationForm
            invitationId={invitationId}
            onSuccess={onSuccessHandler}
          />
        )}
      </LoadLayout>
    </div>
  );
}

export default RegistrationPage;
