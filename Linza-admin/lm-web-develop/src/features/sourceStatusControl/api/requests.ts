import { HTTPError } from "ky";

import { sourceStatusResponseSchema } from "@/entities/sources/models/responses";
import { sourceStatusErrorsSchema } from "@/entities/sources/models/validation";
import apiInstance from "@/shared/api/apiInstance";

export function toggleParsingDataSource(data: {
  dataSourceId: string;
  isActive: boolean;
}) {
  return apiInstance
    .patch(`importer/dataSourceItems/${data.dataSourceId}`, {
      json: { isActive: data.isActive },
    })
    .json()
    .then(sourceStatusResponseSchema.parse)
    .catch(async (error) => {
      if (error instanceof HTTPError && error.response.status === 400) {
        const err = await error.response
          .json()
          .then(sourceStatusErrorsSchema.parse);
        return Promise.reject({
          status: error.response.status,
          errors: err.errors,
        });
      } else {
        return Promise.reject({});
      }
    });
}
