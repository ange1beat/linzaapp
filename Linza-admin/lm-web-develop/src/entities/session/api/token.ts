import { z } from "zod";

import { api } from "@/shared/api";

import { tokenResponse } from "../models/responses";

export async function refreshAuthToken(): Promise<
  z.infer<typeof tokenResponse>
> {
  const result = await api.post("auth/token").json();
  return tokenResponse.parse(result);
}

export function getAuthToken(
  stateToken: string,
): Promise<z.infer<typeof tokenResponse>> {
  return api
    .post("auth/sign-in", { json: { stateToken } })
    .json()
    .then(tokenResponse.parse);
}

export function revokeToken() {
  return api.post("auth/sign-out").json();
}
