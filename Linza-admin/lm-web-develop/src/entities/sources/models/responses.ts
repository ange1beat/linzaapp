import { z } from "zod";

import {
  dataSourceSchema,
  sourceTypeEnum,
} from "@/entities/sources/models/sourceInfo";

export const sourcesResponseSchema = z.object({
  statusCode: z.number(),
  description: z.string(),
  data: z.object({
    pageSize: z.number(),
    page: z.number(),
    count: z.number(),
    dataSourceItems: z.array(dataSourceSchema),
  }),
});

export const sourceStatusResponseSchema = z.object({
  statusCode: z.number(),
  description: z.string(),
  data: z.object({
    title: z.string(),
    description: z.string(),
    iconUri: z.string(),
    type: sourceTypeEnum,
    updateInterval: z.number(),
    config: z.object({}),
    account: z.object({}),
    isAutoCreated: z.boolean(),
    isActive: z.boolean(),
    timezone: z.string(),
    updated: z.string(),
  }),
});
