import React from "react";

import { Card, Table, Text } from "@gravity-ui/uikit";

import {
  StorageBar,
  useStorageQuotasQuery,
  useStorageUsageQuery,
} from "@/entities/storageQuota";
import type { IStorageQuota } from "@/entities/storageQuota";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

const SCOPE_LABELS: Record<string, string> = {
  tenant: "Организация",
  team: "Команда",
  user: "Пользователь",
};

export default function StoragePage() {
  const { data: usage } = useStorageUsageQuery();
  const { data: quotas = [] } = useStorageQuotasQuery();

  const columns = [
    {
      id: "scope_type",
      name: "Тип",
      template: (item: IStorageQuota) =>
        SCOPE_LABELS[item.scope_type] || item.scope_type,
    },
    { id: "scope_id", name: "ID" },
    {
      id: "quota_bytes",
      name: "Квота",
      template: (item: IStorageQuota) => formatBytes(item.quota_bytes),
    },
    {
      id: "used_bytes",
      name: "Использовано",
      template: (item: IStorageQuota) => formatBytes(item.used_bytes),
    },
    {
      id: "percentage",
      name: "%",
      template: (item: IStorageQuota) =>
        item.quota_bytes > 0
          ? `${((item.used_bytes / item.quota_bytes) * 100).toFixed(1)}%`
          : "—",
    },
  ];

  return (
    <div>
      <Text variant="header-1" style={{ marginBottom: 16 }}>
        Хранилище
      </Text>

      {usage && (
        <Card style={{ padding: 16, marginBottom: 16 }}>
          <Text variant="subheader-2" style={{ marginBottom: 12 }}>
            Моё использование
          </Text>
          {usage.user && (
            <StorageBar
              usedBytes={usage.user.used_bytes}
              quotaBytes={usage.user.quota_bytes}
              label="Личная квота"
            />
          )}
          {usage.team && (
            <StorageBar
              usedBytes={usage.team.used_bytes}
              quotaBytes={usage.team.quota_bytes}
              label="Квота команды"
            />
          )}
          {usage.tenant && (
            <StorageBar
              usedBytes={usage.tenant.used_bytes}
              quotaBytes={usage.tenant.quota_bytes}
              label="Квота организации"
            />
          )}
          {!usage.user && !usage.team && !usage.tenant && (
            <Text color="secondary">Квоты не настроены</Text>
          )}
        </Card>
      )}

      <Card>
        <Text variant="subheader-2" style={{ padding: 16 }}>
          Все квоты
        </Text>
        <Table data={quotas} columns={columns} emptyMessage="Нет квот" />
      </Card>
    </div>
  );
}
