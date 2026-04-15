import { ref } from 'vue'
import { useAuth } from './useAuth.js'
import { extractDetectionsPayload } from './detectionsPayload.js'

const reports = ref([])
const loading = ref(false)

/** Нормализует тело POST /api/reports (поддержка legacy { data, filename }). */
function normalizeReportBody(payload) {
  if (payload.report_json != null && typeof payload.report_json === 'string') {
    return payload
  }
  const json = payload.data ?? payload.json
  if (json == null) {
    return {
      filename: payload.filename || 'report.json',
      report_name: payload.report_name || payload.filename || '',
      report_json: '{}',
      match_count: 0,
      status: payload.status || 'success',
      source: payload.source || '',
      started_at: payload.started_at || '',
      finished_at: payload.finished_at || '',
    }
  }
  let matchCount = 0
  let startedAt = payload.started_at || ''
  let finishedAt = payload.finished_at || ''
  try {
    const { list, sourceInfo } = extractDetectionsPayload(json)
    matchCount = list.length
    const ts = sourceInfo?.analysis_timestamp || sourceInfo?.processing_time
    if (ts && !startedAt) startedAt = String(ts)
  } catch {
    /* отчёт без детекций или нестандартная схема */
  }
  return {
    filename: payload.filename || 'video.mp4',
    report_name: payload.report_name || payload.filename || 'report.json',
    source: payload.source || '',
    started_at: startedAt,
    finished_at: finishedAt,
    match_count: matchCount,
    status: payload.status || 'success',
    report_json: typeof json === 'string' ? json : JSON.stringify(json),
  }
}

export function useReports() {
  const { getToken } = useAuth()

  function headers() {
    return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` }
  }

  async function fetchReports() {
    loading.value = true
    try {
      const res = await fetch('/api/reports/', { headers: headers() })
      if (res.ok) reports.value = await res.json()
    } catch {} finally { loading.value = false }
  }

  async function createReport(data) {
    const body = normalizeReportBody(data)
    const res = await fetch('/api/reports/', { method: 'POST', headers: headers(), body: JSON.stringify(body) })
    if (!res.ok) { const d = await res.json().catch(() => ({})); throw new Error(d.detail || 'Error') }
    await fetchReports()
    return await res.json()
  }

  async function getReport(id) {
    const res = await fetch(`/api/reports/${id}`, { headers: headers() })
    if (!res.ok) throw new Error('Not found')
    return await res.json()
  }

  async function patchReport(id, fields) {
    const res = await fetch(`/api/reports/${id}`, {
      method: 'PATCH',
      headers: headers(),
      body: JSON.stringify(fields),
    })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || 'Error')
    }
    await fetchReports()
    return await res.json()
  }

  async function deleteReport(id) {
    const res = await fetch(`/api/reports/${id}`, { method: 'DELETE', headers: headers() })
    if (!res.ok) throw new Error('Error')
    await fetchReports()
  }

  return { reports, loading, fetchReports, createReport, getReport, patchReport, deleteReport }
}
