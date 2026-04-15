import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { telegramFormSchema } from "../models/validation";

export function useTelegramForm(telegram: string = "") {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm({
    resolver: zodResolver(telegramFormSchema),
    values: {
      telegram,
    },
  });
  const { field: telegramField } = useController({
    control: control,
    name: "telegram",
  });

  return {
    telegramField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
  };
}
