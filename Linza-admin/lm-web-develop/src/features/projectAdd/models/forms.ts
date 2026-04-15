import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { nameValidationSchema } from "../models/validation";

export function useNameForm() {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
    reset,
  } = useForm({
    resolver: zodResolver(nameValidationSchema),
    defaultValues: {
      name: "",
    },
  });
  const { field: nameField } = useController({
    control: control,
    name: "name",
  });

  return {
    nameField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
    reset,
  };
}
