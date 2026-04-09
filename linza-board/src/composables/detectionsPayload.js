/** HH:MM:SS / MM:SS / секунды — для аудио-детекций VAF с startFrame=-1. */
function vafTimeToSeconds(v) {
  if (v == null || v === '') return null
  if (typeof v === 'number' && Number.isFinite(v)) return v
  const s = String(v).trim()
  if (!s) return null
  const parts = s.split(':').map((p) => parseFloat(p))
  if (parts.some((x) => Number.isNaN(x))) return null
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2]
  if (parts.length === 2) return parts[0] * 60 + parts[1]
  const x = parseFloat(s)
  return Number.isFinite(x) ? x : null
}

/**
 * Нормализует одну детекцию из формата detector-API / video-ai-filter TIME_BASED
 * (startSeconds/endSeconds, type=audio|video как модальность) в формат VPleer.
 */
function normalizeDetection(d, idx) {
  const base = d != null && typeof d === 'object' ? { ...d } : {}
  if (base.id == null || base.id === '') {
    base.id = `det_${idx}`
  }
  /* VAF: поле type — часто модальность, не подкласс; дублируем в source для плеера */
  if (!base.source && !base.modality) {
    const t = typeof base.type === 'string' ? base.type.toLowerCase() : ''
    if (t === 'audio' || t === 'video') {
      base.source = t
    }
  }
  if (base.start_time !== undefined && base.end_time !== undefined) {
    if (!base.source) {
      base.source = base.modality ? String(base.modality).toLowerCase() : 'both'
    }
  } else {
    Object.assign(base, {
      start_time: base.start_time ?? base.startSeconds ?? 0,
      end_time: base.end_time ?? base.endSeconds ?? 0,
      source: base.source || (base.modality ? String(base.modality).toLowerCase() : 'both'),
    })
  }
  const ss = vafTimeToSeconds(base.start_time)
  const ee = vafTimeToSeconds(base.end_time)
  if (ss != null && ee != null) {
    base.startSeconds = ss
    base.endSeconds = ee
  }
  return base
}

/** result/results в отчёте иногда приходят JSON-строкой */
function parseNestedIfNeeded(v) {
  if (v == null) return null
  if (typeof v === 'string') {
    const t = v.trim()
    if (!t || t === '{}') return null
    try {
      return JSON.parse(t)
    } catch {
      return null
    }
  }
  if (typeof v === 'object') return v
  return null
}

/**
 * Извлекает массив детекций и метаданные из тела отчёта аналитики (любой поддерживаемой формы).
 * Используется в аналитике, плеере и при сохранении отчёта.
 */
export function extractDetectionsPayload(json) {
  if (json == null) {
    throw new Error('Пустой JSON')
  }
  if (Array.isArray(json)) {
    return { list: json, sourceInfo: null }
  }
  if (typeof json !== 'object') {
    throw new Error('Ожидался объект отчёта или массив детекций')
  }
  if (Array.isArray(json.detections)) {
    return {
      list: json.detections,
      sourceInfo: json.sourceInfo || json.source_info || null,
    }
  }
  const nested =
    parseNestedIfNeeded(json.results) ||
    parseNestedIfNeeded(json.result) ||
    parseNestedIfNeeded(json.data)
  if (nested && typeof nested === 'object' && Array.isArray(nested.detections)) {
    return {
      list: nested.detections,
      sourceInfo:
        json.sourceInfo ||
        json.source_info ||
        nested.sourceInfo ||
        nested.source_info ||
        null,
    }
  }
  if (Array.isArray(json.violations)) {
    return {
      list: json.violations,
      sourceInfo: json.sourceInfo || json.source_info || null,
    }
  }
  throw new Error(
    'Нет массива детекций: нужны поле detections, results.detections, violations или JSON-массив.',
  )
}

/**
 * Извлечение + нормализация в VPleer-совместимый формат (start_time, end_time, source, id).
 */
export function extractAndNormalize(json) {
  const { list, sourceInfo } = extractDetectionsPayload(json)
  return { list: list.map(normalizeDetection), sourceInfo }
}
