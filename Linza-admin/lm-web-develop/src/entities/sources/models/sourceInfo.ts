import { z } from "zod";

import {
  SourceExecutionStatus,
  SourceLastResult,
  SourceType,
} from "@/entities/sources/models/types";

export const sourceTypeEnum = z.enum([
  SourceType.VK,
  SourceType.Web,
  SourceType.Telegram,
  SourceType.OK,
]);
export const lastResultEnum = z.enum([
  SourceLastResult.Error,
  SourceLastResult.Success,
]);
export const executionStatus = z.enum([
  SourceExecutionStatus.InProgress,
  SourceExecutionStatus.Stopped,
  SourceExecutionStatus.Planned,
  SourceExecutionStatus.NotConfigure,
]);

export const dataSourceSchema = z.object({
  id: z.string(),
  created: z.string(),
  modified: z.string(),
  title: z.string(),
  description: z.string(),
  iconUri: z.string(),
  type: sourceTypeEnum,
  url: z.string(),
  updateInterval: z.number(),
  isActive: z.boolean(),
  isAutoCreated: z.boolean(),
  config: z.object({}),
  account: z.object({}),
  timezone: z.string(),
  updated: z.string(),
  lastResult: lastResultEnum.optional(),
  nextLaunch: z.number(),
  executionStatus: executionStatus,
});
