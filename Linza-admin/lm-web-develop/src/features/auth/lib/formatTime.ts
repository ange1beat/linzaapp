export function httpDateToMinutes(httpDate: string) {
  const currentDate: Date = new Date();
  const retryAfterDate: Date = new Date(httpDate);

  return Math.ceil(
    (retryAfterDate.getTime() - currentDate.getTime()) / (1000 * 60),
  );
}
