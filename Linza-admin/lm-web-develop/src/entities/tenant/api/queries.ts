import { useQuery } from "@tanstack/react-query";

import { getTenantName } from "./requests";

export function useTenantNameQuery() {
  const { isPending, data } = useQuery({
    queryKey: ["tenant"],
    queryFn: getTenantName,
  });
  return {
    isPending,
    name: data ? data.name : "",
  };
}
