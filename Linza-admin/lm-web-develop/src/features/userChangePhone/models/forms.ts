import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { phoneFormSchema } from "./validation";

export function usePhoneForm() {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm({
    resolver: zodResolver(phoneFormSchema),
    defaultValues: {
      phone: "",
      isValid: false,
    },
  });
  const { field: phoneField } = useController({
    control: control,
    name: "phone",
  });
  const { field: isValidField } = useController({
    control: control,
    name: "isValid",
  });

  return {
    phoneField,
    isValidField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
  };
}
