import { z } from "zod";

import { projectNameSchema } from "@/entities/projects";

export const nameValidationSchema = z.object({
  name: projectNameSchema,
});
