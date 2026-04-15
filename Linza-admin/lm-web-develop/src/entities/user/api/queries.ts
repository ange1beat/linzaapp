import { useQuery } from "@tanstack/react-query";

import { schemaDefaults } from "@/shared/lib/zod";

import { userSchema } from "../models";

import { getUser } from "./requests";

export function useUserQuery() {
  const { isPending, data } = useQuery({
    queryKey: ["user"],
    queryFn: getUser,
  });
  return {
    isPending,
    user: data || schemaDefaults(userSchema),
  };
}
