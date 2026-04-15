import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { emailFormSchema } from "../models/validation";

export function useEmailForm() {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm({
    resolver: zodResolver(emailFormSchema),
    defaultValues: {
      email: "",
    },
  });
  const { field: emailField } = useController({
    control: control,
    name: "email",
  });

  return {
    emailField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
  };
}
