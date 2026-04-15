import { z } from "zod";

import { folderSchema } from "./responses";

export type IFolder = z.infer<typeof folderSchema>;
