const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

/** UUID задачи video-ai-filter: jobId (board) или job_id (экспорт TIME_BASED). */
export function extractVafJobId(obj) {
  if (!obj || typeof obj !== 'object') return ''
  const raw = obj.jobId ?? obj.job_id
  if (typeof raw !== 'string') return ''
  const t = raw.trim()
  return UUID_RE.test(t) ? t : ''
}
