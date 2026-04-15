import { z } from "zod";

import { memberSchema } from "@/entities/members/models/responses";

export type IMember = z.infer<typeof memberSchema>;
