import React from "react";

import { Progress, Text } from "@gravity-ui/uikit";

interface StorageBarProps {
  usedBytes: number;
  quotaBytes: number;
  label?: string;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export function StorageBar({ usedBytes, quotaBytes, label }: StorageBarProps) {
  const percentage = quotaBytes > 0 ? (usedBytes / quotaBytes) * 100 : 0;
  const theme = percentage > 90 ? "danger" : percentage > 70 ? "warning" : "info";

  return (
    <div style={{ marginBottom: 8 }}>
      {label && (
        <Text variant="subheader-1" style={{ marginBottom: 4 }}>
          {label}
        </Text>
      )}
      <Progress value={Math.min(percentage, 100)} theme={theme} size="m" />
      <Text variant="body-1" color="secondary">
        {formatBytes(usedBytes)} / {formatBytes(quotaBytes)} (
        {percentage.toFixed(1)}%)
      </Text>
    </div>
  );
}
