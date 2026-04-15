import { z } from "zod";

export const teamSchema = z.object({
  id: z.number(),
  name: z.string(),
  tenant_id: z.number(),
  member_count: z.number().default(0),
  created_at: z.string().nullable().optional(),
});

export type ITeam = z.infer<typeof teamSchema>;

export const teamMemberSchema = z.object({
  id: z.number(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
  role: z.string(),
});

export type ITeamMember = z.infer<typeof teamMemberSchema>;
