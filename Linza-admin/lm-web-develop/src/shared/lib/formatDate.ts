import { format, parseISO } from "date-fns";

export function formatISODateToCustomFormat(date: string) {
  const parsedDate = parseISO(date);
  return format(parsedDate, "HH:mm dd.MM.yyyy");
}
