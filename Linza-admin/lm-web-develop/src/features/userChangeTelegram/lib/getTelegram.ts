export function getTelegram(tg: string): string {
  let result: string;
  if (tg.startsWith("@")) {
    result = tg;
  } else {
    result = `@${tg}`;
  }
  if (!tg || !tg.length) {
    result = "";
  }
  return result;
}
