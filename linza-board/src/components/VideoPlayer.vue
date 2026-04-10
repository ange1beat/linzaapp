<script setup>
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useAuth } from '../composables/useAuth.js'

/** Резерв в URL: base64(JSON), если коротко; иначе только ds= + postMessage (лимит query / прокси). */
const DETECTIONS_B64_URL_MAX = 6144
const DETECTIONS_COUNT_URL_MAX = 150
const SS_PREFIX = 'linza-vpleer-ds:'

const props = defineProps({
  /** S3-ключ: uploads/… или sources/… */
  filename: { type: String, required: true },
  detections: { type: Array, default: () => [] },
  /** Подпись в шапке (имя файла) */
  title: { type: String, default: '' },
  reportLabel: { type: String, default: '' },
  violationsCount: { type: Number, default: null },
  /** UUID задачи video-ai-filter — для скачивания PDF через board API */
  vafJobId: { type: String, default: '' },
})

const emit = defineEmits(['close'])
const { getToken } = useAuth()
const pdfBusy = ref(false)
const pdfError = ref('')

function encodeStoragePath(storageKey) {
  if (!storageKey) return ''
  return storageKey.split('/').map(encodeURIComponent).join('/')
}

const displayTitle = computed(() => props.title || props.filename.split('/').pop() || props.filename)

function encodeUtf8Base64(value) {
  const s = JSON.stringify(value)
  const bytes = new TextEncoder().encode(s)
  let bin = ''
  for (let i = 0; i < bytes.length; i++) {
    bin += String.fromCharCode(bytes[i])
  }
  return btoa(bin)
}

/** UUID в URL + sessionStorage: один origin (localhost vs 127.0.0.1 ломает postMessage targetOrigin) */
const sessionBridgeId = ref('')

function syncSessionBridge() {
  sessionBridgeId.value = ''
  if (!props.detections.length) return
  const id =
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `ds-${Date.now()}-${Math.random().toString(36).slice(2)}`
  try {
    const detections = JSON.parse(JSON.stringify(props.detections))
    const theme = document.documentElement.getAttribute('data-theme') || 'light'
    sessionStorage.setItem(
      SS_PREFIX + id,
      JSON.stringify({ filename: props.filename, detections, theme }),
    )
    sessionBridgeId.value = id
  } catch (e) {
    console.warn('[VideoPlayer] sessionStorage bridge failed', e)
  }
}

watch(
  () => [props.filename, props.detections],
  syncSessionBridge,
  { deep: true, immediate: true },
)

const src = computed(() => {
  const path = encodeStoragePath(props.filename)
  let base = `/api/vpleer/player/${path}`
  const theme =
    (typeof document !== 'undefined' &&
      document.documentElement.getAttribute('data-theme')) ||
    'light'
  base += `${base.includes('?') ? '&' : '?'}theme=${encodeURIComponent(theme)}`
  const ds = sessionBridgeId.value

  const withDs = (url) => {
    if (!ds) return url
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}ds=${encodeURIComponent(ds)}`
  }

  let url = withDs(base)
  /* Резерв, если ds/postMessage не сработали: короткий отчёт — ?detections= (UTF-8 base64). */
  if (props.detections.length) {
    try {
      const b64 = encodeUtf8Base64(props.detections)
      if (
        b64.length <= DETECTIONS_B64_URL_MAX &&
        props.detections.length <= DETECTIONS_COUNT_URL_MAX
      ) {
        const sep = url.includes('?') ? '&' : '?'
        url = `${url}${sep}detections=${encodeURIComponent(b64)}`
      }
    } catch {
      /* только ds + postMessage */
    }
  }
  return url
})

const iframeRef = ref(null)

function sendDetectionsToFrame() {
  const w = iframeRef.value?.contentWindow
  if (!w || !props.detections.length) return
  /* Дублируем postMessage: ds / ?detections= / сеть могут отставать или не сработать. */
  const theme = document.documentElement.getAttribute('data-theme') || 'light'
  let payload
  try {
    payload = JSON.parse(JSON.stringify(props.detections))
  } catch {
    payload = [...props.detections]
  }
  const msg = {
    type: 'linza-detections',
    filename: props.filename,
    detections: payload,
    theme,
  }
  /* targetOrigin '*' — иначе localhost ≠ 127.0.0.1 и сообщение не уходит */
  w.postMessage(msg, '*')
}

function onPlayerIframeLoad() {
  sendDetectionsToFrame()
  setTimeout(sendDetectionsToFrame, 50)
  setTimeout(sendDetectionsToFrame, 300)
  setTimeout(sendDetectionsToFrame, 800)
}

/** VPleer шлёт linza-vpleer-ready после регистрации listener — иначе postMessage с детекциями теряется (гонка / разный sessionStorage у iframe). */
function onLinzaWindowMessage(ev) {
  if (ev.data?.type !== 'linza-vpleer-ready') return
  if (ev.source !== iframeRef.value?.contentWindow) return
  sendDetectionsToFrame()
}

onMounted(() => {
  window.addEventListener('message', onLinzaWindowMessage)
})
onBeforeUnmount(() => {
  window.removeEventListener('message', onLinzaWindowMessage)
})

async function downloadVafPdf() {
  const jid = (props.vafJobId || '').trim()
  if (!jid) return
  const token = getToken()
  if (!token) {
    pdfError.value = 'Нет сессии — войдите снова'
    return
  }
  pdfError.value = ''
  pdfBusy.value = true
  try {
    const res = await fetch(`/api/reports/vaf-pdf/${encodeURIComponent(jid)}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const t = await res.text().catch(() => '')
      pdfError.value = t.slice(0, 200) || `Ошибка ${res.status}`
      return
    }
    const blob = await res.blob()
    const cd = res.headers.get('Content-Disposition')
    let fname = `linza-report-${jid.slice(0, 8)}.pdf`
    const m = cd && /filename="?([^";]+)"?/i.exec(cd)
    if (m) fname = m[1].trim()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fname
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    pdfError.value = 'Не удалось скачать PDF'
  } finally {
    pdfBusy.value = false
  }
}
</script>

<template>
  <div class="player-overlay">
    <div class="player-shell player-container">
      <header class="player-header">
        <div class="player-head-text">
          <h2 class="player-title">{{ displayTitle }}</h2>
          <p v-if="reportLabel || violationsCount != null" class="player-meta">
            <span v-if="reportLabel">{{ reportLabel }}</span>
            <template v-if="reportLabel && violationsCount != null"> · </template>
            <span v-if="violationsCount != null"
              >Нарушений: <strong>{{ violationsCount }}</strong></span
            >
          </p>
        </div>
        <div class="player-header-actions">
          <button
            v-if="(vafJobId || '').trim()"
            class="btn-pdf"
            type="button"
            :disabled="pdfBusy"
            @click="downloadVafPdf"
          >
            {{ pdfBusy ? 'PDF…' : 'Скачать PDF' }}
          </button>
          <button class="icon-btn close-btn" type="button" title="Закрыть" @click="emit('close')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </header>
      <p v-if="pdfError" class="player-pdf-err">{{ pdfError }}</p>
      <div class="player-frame-wrap">
        <iframe
          ref="iframeRef"
          class="player-iframe"
          title="Просмотр видео"
          :src="src"
          allowfullscreen
          @load="onPlayerIframeLoad"
        />
      </div>
      <p class="player-footnote">Нарушения подсвечены на шкале времени и в списке справа — клик по отрезку или карточке для перехода.</p>
    </div>
  </div>
</template>

<style scoped>
.player-overlay {
  position: fixed;
  inset: 0;
  background: var(--c-modal-overlay, rgba(15, 23, 42, 0.45));
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5000;
  padding: clamp(12px, 3vw, 28px);
}

.player-shell {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  overflow: hidden;
  width: min(1120px, 100%);
  max-height: calc(100vh - 32px);
  display: flex;
  flex-direction: column;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.04);
}

.player-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--c-border);
  background: linear-gradient(180deg, var(--c-surface-2) 0%, var(--c-surface) 100%);
}

.player-head-text {
  min-width: 0;
}

.player-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-txt);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-meta {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--c-txt-2);
}

.icon-btn {
  background: none;
  border: none;
  color: var(--c-txt-2);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--r-lg);
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
}

.icon-btn:hover {
  color: var(--c-txt);
  background: var(--c-surface-2);
}

.player-header-actions {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex-shrink: 0;
}

.btn-pdf {
  margin-top: -2px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  color: var(--c-txt);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.btn-pdf:hover:not(:disabled) {
  background: var(--c-bg);
  border-color: var(--c-blue);
  color: var(--c-blue);
}

.btn-pdf:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.close-btn {
  margin-top: -2px;
}

.player-pdf-err {
  margin: 0;
  padding: 8px 18px;
  font-size: 12px;
  color: var(--c-err, #dc2626);
  background: var(--c-err-bg, rgba(220, 38, 38, 0.08));
  border-bottom: 1px solid var(--c-border);
}

.player-frame-wrap {
  flex: 1;
  min-height: 0;
  background: var(--c-surface-2);
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
}

.player-iframe {
  display: block;
  width: 100%;
  height: min(78vh, 720px);
  min-height: 360px;
  border: none;
}

.player-footnote {
  margin: 0;
  padding: 10px 16px 12px;
  font-size: 11px;
  color: var(--c-txt-3);
  background: var(--c-surface-2);
  border-top: 1px solid var(--c-border);
}
</style>
