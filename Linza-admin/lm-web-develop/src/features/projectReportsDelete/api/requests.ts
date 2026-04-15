import { api } from "@/shared/api";

export function deleteProjectReports(data: {
  projectId: string;
  reportIds: string[];
}) {
  // TODO: If it needed, update request and add validation
  return api.delete(`projects/${data.projectId}/reports`, {
    json: { reportIds: data.reportIds },
  });
}
