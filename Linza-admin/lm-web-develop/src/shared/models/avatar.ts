import { z } from "zod";

import { AVATAR_MAX_SIZE } from "@/shared/config";

export const avatarValidationSchema = z.any().refine((file) => {
  return file?.size <= AVATAR_MAX_SIZE * 1024;
}, "avatar-oversize");

export const newAvatarErrors = z.object({
  errors: z.object({
    file: z.array(z.string()),
  }),
});
