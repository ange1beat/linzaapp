import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { otpFormSchema } from "./validation";

export function useOTPForm() {
  const {
    handleSubmit,
    control,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm({
    resolver: zodResolver(otpFormSchema),
    defaultValues: {
      otp: "",
    },
  });
  const { field: otpField } = useController({
    control: control,
    name: "otp",
  });

  return {
    otpField,
    handleSubmit,
    errors,
    setError,
    clearErrors,
  };
}
