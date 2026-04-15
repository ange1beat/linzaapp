import { useQuery } from "@tanstack/react-query";

import { getSources } from "@/entities/sources/api/requests";

export function useGetSourcesQuery(queryData: {
  search?: string;
  pageNumber: number;
  pageSize: number;
  sortBy?: string;
  filterValues?: { [k: string]: string[] };
}) {
  const { search, pageNumber, pageSize, sortBy, filterValues } = queryData;
  const { data, isPending } = useQuery({
    queryKey: [
      "sources",
      { search, pageNumber, pageSize, sortBy, filterValues },
    ],
    queryFn: () =>
      getSources({ search, pageNumber, pageSize, sortBy, filterValues }),
  });
  return {
    sources: data?.data.dataSourceItems ?? [],
    total: data?.data.count ?? 0,
    isPending,
  };
}
