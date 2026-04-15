export function getTelegramLink(data: string) {
  const telegramName = data.replaceAll("@", "");
  return `https://t.me/${telegramName}`;
}
