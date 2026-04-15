import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createStorageQuota,
  deleteStorageQuota,
  getStorageQuotas,
  getStorageUsage,
  updateStorageQuota,
} from "./requests";

export const useStorageQuotasQuery = (scopeType?: string) =>
  useQuery({
    queryKey: ["storage-quotas", scopeType],
    queryFn: () => getStorageQuotas(scopeType),
  });

export const useStorageUsageQuery = () =>
  useQuery({
    queryKey: ["storage-usage"],
    queryFn: getStorageUsage,
  });

export const useCreateQuotaMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createStorageQuota,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["storage-quotas"] }),
  });
};

export const useUpdateQuotaMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      scopeType,
      scopeId,
      quotaBytes,
    }: {
      scopeType: string;
      scopeId: number;
      quotaBytes: number;
    }) => updateStorageQuota(scopeType, scopeId, quotaBytes),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["storage-quotas"] }),
  });
};

export const useDeleteQuotaMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      scopeType,
      scopeId,
    }: {
      scopeType: string;
      scopeId: number;
    }) => deleteStorageQuota(scopeType, scopeId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["storage-quotas"] }),
  });
};
