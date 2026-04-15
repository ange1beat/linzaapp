import { zodResolver } from "@hookform/resolvers/zod";
import { useController, useForm } from "react-hook-form";

import { newMemberSchema } from "@/features/memberAdd/models/validation";

export function useMemberAddForm(email: string = "") {
  const {
    handleSubmit,
    control,
    setError,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      email: email,
    },
    resolver: zodResolver(newMemberSchema),
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
    reset,
  };
}
