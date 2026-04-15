import apiInstance from "@/shared/api/apiInstance";

export function deleteSourceById(sourceId: string) {
  return apiInstance.delete(`importer/dataSourceItems/${sourceId}`).json();
}
