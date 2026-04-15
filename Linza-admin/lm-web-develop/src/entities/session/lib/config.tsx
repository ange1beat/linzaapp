import ky from "ky";

import { api } from "@/shared/api";

import { refreshAuthToken } from "../api/token";
import { addToken, delToken, getTokens } from "../models/stores";

function addJwtToken(request: Request) {
  const { accessToken } = getTokens();
  request.headers.set("Authorization", `Bearer ${accessToken}`);
}

class AccessToken {
  private isRefreshing = false;

  private queue: ((value?: typeof ky.stop) => void)[] = [];

  refresh = () => {
    const promise = new Promise<typeof ky.stop | undefined>((resolve) => {
      this.queue.push(resolve);
    });
    if (!this.isRefreshing) {
      this.apiCall();
    }
    return promise;
  };

  private apiCall = async () => {
    this.isRefreshing = true;
    const { accessToken: token } = getTokens();
    if (token) {
      try {
        const { accessToken } = await refreshAuthToken();
        addToken(accessToken);
        this.queue.forEach((resolve) => resolve());
      } catch {
        delToken();
        this.queue.forEach((resolve) => resolve(ky.stop));
      } finally {
        this.queue = [];
        this.isRefreshing = false;
      }
    } else {
      delToken();
    }
  };
}

api.updateConfig({
  retry: {
    statusCodes: [401],
  },
  hooks: {
    beforeRequest: [addJwtToken],
    beforeRetry: [new AccessToken().refresh],
  },
});
