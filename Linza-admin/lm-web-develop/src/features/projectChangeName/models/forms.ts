import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { nameValidationSchema } from "../models/validation";

export function useNameForm(projectName: string) {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm({
    resolver: zodResolver(nameValidationSchema),
    values: {
      name: projectName,
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
  };
}
