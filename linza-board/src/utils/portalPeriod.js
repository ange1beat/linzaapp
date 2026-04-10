/** Общие подписи периода для экранов портала (главный редактор). */

export const PORTAL_PERIODS = [
  { key: 'week', label: 'Неделя' },
  { key: 'month', label: 'Месяц' },
  { key: 'quarter', label: 'Квартал' },
  { key: 'year', label: 'Год' },
]

/**
 * @param {string} periodKey
 * @param {number} [periodDays] — из ответа API metrics/summary
 */
export function portalPeriodSubtitle(periodKey, periodDays) {
  const fallback = { week: 7, month: 30, quarter: 91, year: 365 }
  const d = periodDays ?? fallback[periodKey] ?? 30
  return `Период: последние ${d} дней`
}
