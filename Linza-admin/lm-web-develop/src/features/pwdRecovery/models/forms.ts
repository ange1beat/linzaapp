import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { passwordMatchSchema } from "../models/validation";

export function useSetPasswordForm() {
  const {
    handleSubmit,
    control,
    formState: { errors },
    clearErrors,
    setError,
    watch,
  } = useForm({
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
    resolver: zodResolver(passwordMatchSchema),
  });

  const { field: passwordField } = useController({
    control: control,
    name: "password",
  });
  const { field: confirmPasswordField } = useController({
    control: control,
    name: "confirmPassword",
  });

  return {
    passwordField,
    confirmPasswordField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
    watch,
  };
}
