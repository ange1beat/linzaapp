import { z } from "zod";

import { sourcesResponseSchema } from "@/entities/sources/models/responses";
import { api } from "@/shared/api";

export function getSources(sourcesData: {
  pageNumber: number;
  pageSize: number;
  search?: string;
  sortBy?: string;
  filterValues?: { [k: string]: string[] };
}): Promise<z.infer<typeof sourcesResponseSchema>> {
  const searchParams = new URLSearchParams();
  sourcesData.search && searchParams.set("url", sourcesData.search);
  searchParams.set("pageSize", sourcesData.pageSize.toString());
  searchParams.set("page", sourcesData.pageNumber.toString());
  sourcesData.sortBy && searchParams.set("sortBy", sourcesData.sortBy);
  if (sourcesData.filterValues) {
    Object.entries(sourcesData.filterValues).forEach(([key, values]) => {
      values.forEach((value) => {
        searchParams.append(key, value);
      });
    });
  }
  return api.get("importer/dataSourceItems/search", { searchParams }).json();
}
