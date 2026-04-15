import { z } from "zod";

import { userSchema } from "./responses";

export type IUser = z.infer<typeof userSchema>;
