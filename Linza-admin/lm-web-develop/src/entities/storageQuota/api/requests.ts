import { api } from "@/shared/api";

import type { IStorageQuota, IStorageUsage } from "../models/models";

export const getStorageQuotas = (
  scopeType?: string,
): Promise<IStorageQuota[]> => {
  const params = scopeType ? `?scope_type=${scopeType}` : "";
  return api.get(`storage/quotas${params}`).json<IStorageQuota[]>();
};

export const createStorageQuota = (data: {
  scope_type: string;
  scope_id: number;
  quota_bytes: number;
}): Promise<IStorageQuota> =>
  api.post("storage/quotas", { json: data }).json<IStorageQuota>();

export const updateStorageQuota = (
  scopeType: string,
  scopeId: number,
  quotaBytes: number,
): Promise<IStorageQuota> =>
  api
    .put(`storage/quotas/${scopeType}/${scopeId}`, {
      json: { quota_bytes: quotaBytes },
    })
    .json<IStorageQuota>();

export const deleteStorageQuota = (
  scopeType: string,
  scopeId: number,
): Promise<void> =>
  api
    .delete(`storage/quotas/${scopeType}/${scopeId}`)
    .then(() => undefined);

export const getStorageUsage = (): Promise<IStorageUsage> =>
  api.get("storage/usage").json<IStorageUsage>();
