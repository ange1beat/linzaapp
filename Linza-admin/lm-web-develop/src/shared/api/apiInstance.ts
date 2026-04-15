import ky, { KyInstance, Options } from "ky";

import env from "../config/env";

class API {
  private client: KyInstance;

  constructor() {
    this.client = ky.create({ prefixUrl: env.API_URL });
  }

  updateConfig(config: Options) {
    this.client = this.client.extend(config);
  }

  get get() {
    return this.client.get;
  }

  get post() {
    return this.client.post;
  }

  get put() {
    return this.client.put;
  }

  get patch() {
    return this.client.patch;
  }

  get delete() {
    return this.client.delete;
  }
}

export default new API();
