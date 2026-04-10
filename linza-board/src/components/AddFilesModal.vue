<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth.js'

const props = defineProps({
  /** Стартовая вкладка при открытии (например после OAuth — 'yandex'). */
  initialSource: {
    type: String,
    default: 'file',
  },
})

const emit = defineEmits([
  'close',
  'upload-url',
  'upload-file',
  'import-s3',
  'import-yandex-me',
  'import-google-me',
  'cloud-integrations-changed',
])
const { getToken } = useAuth()

function authJsonHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`,
  }
}

const VALID_SOURCES = new Set(['file', 'yandex', 'google', 's3', 'url'])
const source = ref('file') // 'file' | 'yandex' | 'google' | 's3' | 'url'

/** Разрешённые способы из org-config (мастер администратора); до ответа API — все. */
const sourcesEnabled = ref(['local', 'yadisk', 'google', 's3'])

function hasIngest(id) {
  return sourcesEnabled.value.includes(id)
}

function isTabAllowed(tab) {
  if (tab === 'file' || tab === 'url') return hasIngest('local')
  if (tab === 'yandex') return hasIngest('yadisk')
  if (tab === 'google') return hasIngest('google')
  if (tab === 's3') return hasIngest('s3')
  return false
}

function firstAllowedTab() {
  for (const t of ['file', 'url', 'yandex', 'google', 's3']) {
    if (isTabAllowed(t)) return t
  }
  return 'file'
}

const ingestHintText = computed(() => {
  const loc = hasIngest('local')
  const names = []
  if (hasIngest('yadisk')) names.push('Яндекс')
  if (hasIngest('google')) names.push('Google')
  if (hasIngest('s3')) names.push('S3')
  const hasS3 = hasIngest('s3')
  const inner =
    names.length > 0 ? names.join(', ') + (hasS3 ? ' — профили S3 в «Настройках»' : '') : ''
  if (loc && names.length) return `С устройства, по ссылке или из облака (${inner}).`
  if (loc) return 'С устройства или по ссылке.'
  if (names.length) return `Импорт из облака (${inner}).`
  return 'Добавление файлов в хранилище.'
})

async function loadIngestSources() {
  try {
    const token = getToken()
    if (!token) return
    const res = await fetch('/api/portal/ingest-sources', {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    })
    if (res.ok) {
      const data = await res.json().catch(() => ({}))
      const arr = Array.isArray(data.sources_enabled) ? data.sources_enabled : []
      if (arr.length) sourcesEnabled.value = arr
    }
  } catch {
    // оставляем дефолт
  } finally {
    syncSourceFromProps()
  }
}

/** Личный Яндекс.Диск (OAuth пользователя) */
const yandexConnected = ref(false)
const yandexStatusLoading = ref(false)
const yandexStatusError = ref('')
const yandexObjects = ref([])
const yandexLoading = ref(false)
const yandexError = ref('')
const yandexSelectedKeys = ref([])
const yandexRoot = ref('')
const yandexPrefix = ref('')
const yandexResultsEl = ref(null)
/** После запроса списка: 200 и пустой массив — показать подсказку, а не «пустоту». */
const yandexShowEmptyHint = ref(false)

/** Личный Google Диск (OAuth пользователя) */
const googleConnected = ref(false)
const googleStatusLoading = ref(false)
const googleStatusError = ref('')
const googleObjects = ref([])
const googleLoading = ref(false)
const googleError = ref('')
const googleSelectedKeys = ref([])
const googleFolderId = ref('')
const googleNameHint = ref('')
const googleResultsEl = ref(null)
const googleShowEmptyHint = ref(false)

// ── URL tab ───────────────────────────────────────────────────────────────────
const url = ref('')
const urlError = ref('')

function submitUrl() {
  const trimmed = url.value.trim()
  if (!trimmed) {
    urlError.value = 'Введите ссылку'
    return
  }
  try {
    new URL(trimmed)
  } catch {
    urlError.value = 'Некорректная ссылка'
    return
  }
  urlError.value = ''
  emit('upload-url', trimmed)
}

// ── Local file tab — только видео и аудио ────────────────────────────────────
const fileInput = ref(null)
const fileError = ref('')

const LOCAL_FILE_ACCEPT =
  'video/*,audio/*,.mp4,.avi,.mkv,.mov,.webm,.m4v,.wmv,.mpeg,.mpg,.3gp,.ts,.mp3,.wav,.aac,.m4a,.flac,.ogg,.opus,.wma,.oga'

const MEDIA_EXT_RE =
  /\.(mp4|avi|mkv|mov|webm|m4v|wmv|mpeg|mpg|mpe|3gp|ts|mts|m2ts|mp3|wav|aac|m4a|flac|ogg|opus|wma|aiff?|oga)$/i

function isAllowedMediaFile(file) {
  const t = (file.type || '').toLowerCase()
  if (t.startsWith('video/') || t.startsWith('audio/')) return true
  return MEDIA_EXT_RE.test(file.name || '')
}

function pickFile() {
  fileInput.value?.click()
}

function onFileChange(e) {
  fileError.value = ''
  const f = e.target.files?.[0]
  if (!f) return
  if (!isAllowedMediaFile(f)) {
    fileError.value = 'Можно загружать только видео и аудио (например MP4, MOV, MKV, MP3, WAV…).'
    e.target.value = ''
    return
  }
  emit('upload-file', f)
  e.target.value = ''
}

// ── Remote S3 tab ─────────────────────────────────────────────────────────────
/** saved — профиль из настроек; manual — разовый ввод */
const s3InputMode = ref('saved')
const sourceProfiles = ref([])
const profilesLoading = ref(false)
const profilesLoadError = ref('')
const selectedProfileId = ref(null)

const rEndpoint = ref('')
const rBucket = ref('')
const rRegion = ref('ru-1')
const rAccessKey = ref('')
const rSecret = ref('')
const rPrefix = ref('')

const remoteObjects = ref([])
const remoteLoading = ref(false)
const remoteError = ref('')
/** массив ключей — надёжнее для :checked, чем Ref(Set) */
const selectedKeys = ref([])
const remoteResultsEl = ref(null)

const videoExt = /\.(mp4|avi|mkv|mov|webm|m4v|wmv)$/i

const listParams = computed(() => ({
  endpoint_url: rEndpoint.value.trim(),
  bucket_name: rBucket.value.trim(),
  access_key_id: rAccessKey.value.trim(),
  secret_access_key: rSecret.value,
  region: rRegion.value.trim() || 'ru-1',
  prefix: rPrefix.value.trim(),
  max_keys: 500,
}))

function resetS3ListState() {
  remoteObjects.value = []
  selectedKeys.value = []
  remoteError.value = ''
}

async function loadSourceProfiles() {
  profilesLoading.value = true
  profilesLoadError.value = ''
  try {
    const res = await fetch('/api/files/remote-s3/source-profiles', {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    sourceProfiles.value = await res.json()
    if (!sourceProfiles.value.length) {
      s3InputMode.value = 'manual'
      selectedProfileId.value = null
    } else if (s3InputMode.value === 'saved') {
      const cur = selectedProfileId.value
      const ok = cur && sourceProfiles.value.some(p => p.id === cur)
      selectedProfileId.value = ok ? cur : sourceProfiles.value[0].id
    }
  } catch (e) {
    profilesLoadError.value = e.message || 'Не удалось загрузить профили'
    sourceProfiles.value = []
    s3InputMode.value = 'manual'
    selectedProfileId.value = null
  } finally {
    profilesLoading.value = false
  }
}

function onS3ModeChange(mode) {
  s3InputMode.value = mode
  resetS3ListState()
  if (mode === 'saved' && sourceProfiles.value.length) {
    const cur = selectedProfileId.value
    const ok = cur && sourceProfiles.value.some(p => p.id === cur)
    selectedProfileId.value = ok ? cur : sourceProfiles.value[0].id
  }
}

function onProfileSelectChange() {
  resetS3ListState()
}

watch(
  () => source.value,
  v => {
    if (v === 's3') loadSourceProfiles()
    if (v === 'yandex') loadYandexStatus()
    if (v === 'google') loadGoogleStatus()
  },
)

watch(
  () => ({
    tab: source.value,
    yandexConnected: yandexConnected.value,
    yandexStatusLoading: yandexStatusLoading.value,
    googleConnected: googleConnected.value,
    googleStatusLoading: googleStatusLoading.value,
  }),
  async ({ tab, yandexConnected, yandexStatusLoading, googleConnected, googleStatusLoading }) => {
    if (tab === 'yandex' && !yandexStatusLoading && yandexConnected) await fetchYandexList()
    if (tab === 'google' && !googleStatusLoading && googleConnected) await fetchGoogleList()
  },
)

async function loadYandexStatus() {
  yandexStatusLoading.value = true
  yandexStatusError.value = ''
  try {
    const res = await fetch('/api/integrations/yandex/status', {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const data = await res.json()
    yandexConnected.value = !!data.connected
  } catch (e) {
    yandexStatusError.value = e.message || 'Не удалось проверить Яндекс'
    yandexConnected.value = false
  } finally {
    yandexStatusLoading.value = false
  }
}

async function startYandexLogin() {
  yandexStatusError.value = ''
  try {
    const res = await fetch('/api/integrations/yandex/start', {
      method: 'POST',
      headers: authJsonHeaders(),
      body: JSON.stringify({ frontend_origin: window.location.origin }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`)
    }
    if (data.authorize_url) {
      window.location.href = data.authorize_url
    }
  } catch (e) {
    yandexStatusError.value = e.message || 'Не удалось начать вход'
  }
}

async function yandexDisconnect() {
  if (!confirm('Отключить Яндекс.Диск для этого аккаунта?')) return
  try {
    const res = await fetch('/api/integrations/yandex/disconnect', {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) throw new Error('Ошибка отключения')
    yandexConnected.value = false
    yandexObjects.value = []
    yandexSelectedKeys.value = []
    yandexShowEmptyHint.value = false
    emit('cloud-integrations-changed')
  } catch (e) {
    yandexStatusError.value = e.message
  }
}

function resetYandexListState() {
  yandexObjects.value = []
  yandexSelectedKeys.value = []
  yandexError.value = ''
}

function toggleYandexKey(k, checked) {
  const cur = yandexSelectedKeys.value
  if (checked && !cur.includes(k)) {
    yandexSelectedKeys.value = [...cur, k]
  } else if (!checked && cur.includes(k)) {
    yandexSelectedKeys.value = cur.filter(x => x !== k)
  }
}

function yandexSelectAll() {
  yandexSelectedKeys.value = yandexObjects.value.map(o => o.key)
}

function yandexSelectVideosOnly() {
  yandexSelectedKeys.value = yandexObjects.value
    .filter(o => videoExt.test(o.key))
    .map(o => o.key)
}

function yandexClearSelection() {
  yandexSelectedKeys.value = []
}

async function fetchYandexList() {
  yandexError.value = ''
  yandexShowEmptyHint.value = false
  yandexLoading.value = true
  yandexObjects.value = []
  yandexSelectedKeys.value = []
  try {
    const res = await fetch('/api/integrations/yandex/files/list', {
      method: 'POST',
      headers: authJsonHeaders(),
      body: JSON.stringify({
        root_path: yandexRoot.value.trim(),
        prefix: yandexPrefix.value.trim(),
        max_keys: 500,
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const data = await res.json()
    yandexObjects.value = data.objects || []
    yandexShowEmptyHint.value = yandexObjects.value.length === 0
    if (data.is_truncated) {
      yandexError.value = 'Показана только часть списка. Уточните папку или префикс.'
    }
    await nextTick()
    yandexResultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    yandexError.value = e.message
  } finally {
    yandexLoading.value = false
  }
}

function submitYandexImport() {
  const keys = [...yandexSelectedKeys.value]
  if (!keys.length) {
    yandexError.value = 'Выберите хотя бы один файл'
    return
  }
  yandexError.value = ''
  emit('import-yandex-me', { keys })
}

async function loadGoogleStatus() {
  googleStatusLoading.value = true
  googleStatusError.value = ''
  try {
    const token = getToken()
    if (!token) {
      throw new Error('Нет сессии Linza — войдите в приложение снова и повторите вход Google.')
    }
    const res = await fetch('/api/integrations/google/status', {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    })
    if (res.status === 401) {
      throw new Error(
        'Сессия Linza истекла (во время входа Google). Обновите страницу, войдите в Linza снова, затем «Войти через Google».',
      )
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      const d = err.detail
      const msg =
        typeof d === 'string' ? d : Array.isArray(d) ? d.map(x => x.msg || x).join('; ') : `HTTP ${res.status}`
      throw new Error(msg || `HTTP ${res.status}`)
    }
    const data = await res.json().catch(() => ({}))
    const raw = data?.connected
    googleConnected.value = raw === true || raw === 'true' || raw === 1
    if (googleConnected.value) {
      googleStatusError.value = ''
    }
  } catch (e) {
    googleStatusError.value = e.message || 'Не удалось проверить Google'
    googleConnected.value = false
  } finally {
    googleStatusLoading.value = false
  }
}

function setSourceTab(s) {
  if (!VALID_SOURCES.has(s) || !isTabAllowed(s)) return
  source.value = s
}

/** Открытие с нужной вкладкой (OAuth-редиректы: yandex / google). */
function syncSourceFromProps() {
  const v = props.initialSource
  const want = typeof v === 'string' && VALID_SOURCES.has(v) ? v : 'file'
  source.value = isTabAllowed(want) ? want : firstAllowedTab()
}

watch(() => props.initialSource, syncSourceFromProps, { immediate: true })

onMounted(() => {
  loadIngestSources()
})

defineExpose({
  reloadGoogleConnection: async () => {
    await loadGoogleStatus()
    if (googleConnected.value && source.value === 'google') await fetchGoogleList()
  },
  reloadYandexConnection: async () => {
    await loadYandexStatus()
    if (yandexConnected.value && source.value === 'yandex') await fetchYandexList()
  },
})

async function startGoogleLogin() {
  googleStatusError.value = ''
  try {
    const res = await fetch('/api/integrations/google/start', {
      method: 'POST',
      headers: authJsonHeaders(),
      body: JSON.stringify({ frontend_origin: window.location.origin }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`)
    }
    if (data.authorize_url) {
      window.location.href = data.authorize_url
    }
  } catch (e) {
    googleStatusError.value = e.message || 'Не удалось начать вход'
  }
}

async function googleDisconnect() {
  if (!confirm('Отключить Google Диск для этого аккаунта?')) return
  try {
    const res = await fetch('/api/integrations/google/disconnect', {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) throw new Error('Ошибка отключения')
    googleConnected.value = false
    googleObjects.value = []
    googleSelectedKeys.value = []
    googleShowEmptyHint.value = false
    emit('cloud-integrations-changed')
  } catch (e) {
    googleStatusError.value = e.message
  }
}

function toggleGoogleKey(k, checked) {
  const cur = googleSelectedKeys.value
  if (checked && !cur.includes(k)) {
    googleSelectedKeys.value = [...cur, k]
  } else if (!checked && cur.includes(k)) {
    googleSelectedKeys.value = cur.filter(x => x !== k)
  }
}

function googleSelectAll() {
  googleSelectedKeys.value = googleObjects.value.map(o => o.key)
}

function googleSelectVideosOnly() {
  googleSelectedKeys.value = googleObjects.value
    .filter(o => videoExt.test(o.name || o.key))
    .map(o => o.key)
}

function googleClearSelection() {
  googleSelectedKeys.value = []
}

async function fetchGoogleList() {
  googleError.value = ''
  googleShowEmptyHint.value = false
  googleLoading.value = true
  googleObjects.value = []
  googleSelectedKeys.value = []
  try {
    const res = await fetch('/api/integrations/google/files/list', {
      method: 'POST',
      headers: authJsonHeaders(),
      body: JSON.stringify({
        root_path: googleFolderId.value.trim(),
        prefix: googleNameHint.value.trim(),
        max_keys: 500,
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const data = await res.json()
    googleObjects.value = data.objects || []
    googleShowEmptyHint.value = googleObjects.value.length === 0
    if (data.is_truncated) {
      googleError.value = 'Показана только часть списка. Уточните папку или имя.'
    }
    await nextTick()
    googleResultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    googleError.value = e.message
  } finally {
    googleLoading.value = false
  }
}

function submitGoogleImport() {
  const keys = [...googleSelectedKeys.value]
  if (!keys.length) {
    googleError.value = 'Выберите хотя бы один файл'
    return
  }
  googleError.value = ''
  emit('import-google-me', { keys })
}

function displayRemoteName(o) {
  return (o && (o.name || o.key)) || ''
}

function toggleRemoteKey(k, checked) {
  const cur = selectedKeys.value
  if (checked && !cur.includes(k)) {
    selectedKeys.value = [...cur, k]
  } else if (!checked && cur.includes(k)) {
    selectedKeys.value = cur.filter(x => x !== k)
  }
}

function selectAll() {
  selectedKeys.value = remoteObjects.value.map(o => o.key)
}

function selectVideosOnly() {
  selectedKeys.value = remoteObjects.value
    .filter(o => videoExt.test(o.key))
    .map(o => o.key)
}

function clearSelection() {
  selectedKeys.value = []
}

async function fetchRemoteList() {
  remoteError.value = ''
  remoteLoading.value = true
  remoteObjects.value = []
  selectedKeys.value = []
  const useProfile = s3InputMode.value === 'saved' && selectedProfileId.value != null
  if (useProfile) {
    try {
      const res = await fetch('/api/files/remote-s3/list-by-profile', {
        method: 'POST',
        headers: authJsonHeaders(),
        body: JSON.stringify({
          profile_id: selectedProfileId.value,
          prefix: rPrefix.value.trim(),
          max_keys: 500,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()
      remoteObjects.value = data.objects || []
      if (data.is_truncated) {
        remoteError.value = 'Показана только первая порция объектов (до 500). Уточните префикс.'
      }
      await nextTick()
      remoteResultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } catch (e) {
      remoteError.value = e.message
    } finally {
      remoteLoading.value = false
    }
    return
  }

  const p = listParams.value
  if (!p.endpoint_url || !p.bucket_name || !p.access_key_id || !p.secret_access_key) {
    remoteError.value = 'Заполните эндпоинт, бакет, ключ и секрет'
    remoteLoading.value = false
    return
  }
  try {
    const res = await fetch('/api/files/remote-s3/list', {
      method: 'POST',
      headers: authJsonHeaders(),
      body: JSON.stringify(p),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const data = await res.json()
    remoteObjects.value = data.objects || []
    if (data.is_truncated) {
      remoteError.value = 'Показана только первая порция объектов (до 500). Уточните префикс.'
    }
    await nextTick()
    remoteResultsEl.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    remoteError.value = e.message
  } finally {
    remoteLoading.value = false
  }
}

function submitRemoteImport() {
  const keys = [...selectedKeys.value]
  if (!keys.length) {
    remoteError.value = 'Выберите хотя бы один объект'
    return
  }
  remoteError.value = ''
  const useProfile = s3InputMode.value === 'saved' && selectedProfileId.value != null
  if (useProfile) {
    emit('import-s3', { profile_id: selectedProfileId.value, keys })
    return
  }
  emit('import-s3', {
    endpoint_url: rEndpoint.value.trim(),
    bucket_name: rBucket.value.trim(),
    access_key_id: rAccessKey.value.trim(),
    secret_access_key: rSecret.value,
    region: rRegion.value.trim() || 'ru-1',
    keys,
  })
}

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes === 0) return '0 Б'
  const u = ['Б', 'КБ', 'МБ', 'ГБ']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(i ? 1 : 0)} ${u[i]}`
}
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>Добавить в хранилище</h2>
        <button type="button" class="close-btn" @click="emit('close')">&times;</button>
      </div>

      <p class="single-mode-hint">
        {{ ingestHintText }}
      </p>

      <div class="tabs" role="tablist">
        <button
          v-if="hasIngest('local')"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: source === 'file' }"
          @click="setSourceTab('file')"
        >
          Файл
        </button>
        <button
          v-if="hasIngest('local')"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: source === 'url' }"
          @click="setSourceTab('url')"
        >
          Ссылка
        </button>
        <button
          v-if="hasIngest('yadisk')"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: source === 'yandex' }"
          @click="setSourceTab('yandex')"
        >
          Яндекс
        </button>
        <button
          v-if="hasIngest('google')"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: source === 'google' }"
          @click="setSourceTab('google')"
        >
          Google
        </button>
        <button
          v-if="hasIngest('s3')"
          type="button"
          role="tab"
          class="tab"
          :class="{ active: source === 's3' }"
          @click="setSourceTab('s3')"
        >
          S3
        </button>
      </div>

      <!-- Локальный файл -->
      <div v-show="source === 'file'" class="modal-body">
        <p class="hint">Можно выбрать только <strong>видео</strong> и <strong>аудио</strong>.</p>
        <input
          ref="fileInput"
          type="file"
          class="hidden-input"
          :accept="LOCAL_FILE_ACCEPT"
          @change="onFileChange"
        />
        <div v-if="fileError" class="field-error">{{ fileError }}</div>
        <button type="button" class="btn primary wide" @click="pickFile">Выбрать файл…</button>
      </div>

      <!-- URL -->
      <div v-show="source === 'url'" class="modal-body">
        <label class="field-label">Ссылка на файл</label>
        <input
          v-model="url"
          type="url"
          class="field-input"
          placeholder="https://…"
          @keydown.enter.prevent="submitUrl"
        />
        <div v-if="urlError" class="field-error">{{ urlError }}</div>
        <button type="button" class="btn primary wide" @click="submitUrl">Добавить по ссылке</button>
      </div>

      <!-- Яндекс.Диск -->
      <div v-show="source === 'yandex'" class="modal-body">
        <div v-if="yandexStatusLoading" class="muted-inline">Проверка подключения…</div>
        <template v-else-if="!yandexConnected">
          <p class="muted-inline">Подключите Яндекс.Диск, чтобы выбрать файлы в облаке.</p>
          <div v-if="yandexStatusError" class="field-error">{{ yandexStatusError }}</div>
          <button type="button" class="btn primary wide" @click="startYandexLogin">Войти через Яндекс</button>
        </template>
        <template v-else>
          <div class="yandex-connected-row">
            <span class="muted-inline" style="margin: 0">Яндекс.Диск подключён</span>
            <button type="button" class="btn-link danger" @click="yandexDisconnect">Отключить</button>
          </div>
          <label class="field-label">Корневая папка (необязательно)</label>
          <input v-model="yandexRoot" type="text" class="field-input" placeholder="/" />
          <label class="field-label">Префикс / фильтр</label>
          <input v-model="yandexPrefix" type="text" class="field-input" placeholder="video/" />
          <div class="row-actions">
            <button type="button" class="btn primary" :disabled="yandexLoading" @click="fetchYandexList">
              {{ yandexLoading ? 'Загрузка…' : 'Показать файлы' }}
            </button>
          </div>
          <div v-if="yandexError" class="field-error">{{ yandexError }}</div>
          <div ref="yandexResultsEl" class="remote-list">
            <div v-if="yandexShowEmptyHint && !yandexLoading" class="remote-list-notice">
              <span class="remote-list-notice-icon">i</span>
              <span>Список пуст. Укажите другую папку или префикс.</span>
            </div>
            <template v-if="yandexObjects.length">
              <div class="list-toolbar">
                <span class="muted">{{ yandexSelectedKeys.length }} выбрано</span>
                <button type="button" class="btn small" @click="yandexSelectAll">Все</button>
                <button type="button" class="btn small" @click="yandexSelectVideosOnly">Только видео</button>
                <button type="button" class="btn small" @click="yandexClearSelection">Сброс</button>
              </div>
              <div class="obj-rows">
                <label v-for="o in yandexObjects" :key="o.key" class="obj-row">
                  <input
                    type="checkbox"
                    class="remote-obj-checkbox"
                    :checked="yandexSelectedKeys.includes(o.key)"
                    @change="toggleYandexKey(o.key, ($event.target).checked)"
                  />
                  <span class="obj-key">{{ o.key }}</span>
                  <span class="obj-size">{{ fmtSize(o.size) }}</span>
                </label>
              </div>
              <button type="button" class="btn primary wide" @click="submitYandexImport">Импортировать в Linza</button>
            </template>
          </div>
        </template>
      </div>

      <!-- Google Диск -->
      <div v-show="source === 'google'" class="modal-body">
        <div v-if="googleStatusLoading" class="muted-inline">Проверка подключения…</div>
        <template v-else-if="!googleConnected">
          <p class="muted-inline">Подключите Google Диск, чтобы выбрать файлы в облаке.</p>
          <div v-if="googleStatusError" class="field-error">{{ googleStatusError }}</div>
          <button type="button" class="btn primary wide" @click="startGoogleLogin">Войти через Google</button>
        </template>
        <template v-else>
          <div class="yandex-connected-row">
            <span class="muted-inline" style="margin: 0">Google Диск подключён</span>
            <button type="button" class="btn-link danger" @click="googleDisconnect">Отключить</button>
          </div>
          <label class="field-label">ID папки (необязательно)</label>
          <input v-model="googleFolderId" type="text" class="field-input" placeholder="из URL Google Drive" />
          <label class="field-label">Фильтр по имени</label>
          <input v-model="googleNameHint" type="text" class="field-input" placeholder="часть имени файла" />
          <div class="row-actions">
            <button type="button" class="btn primary" :disabled="googleLoading" @click="fetchGoogleList">
              {{ googleLoading ? 'Загрузка…' : 'Показать файлы' }}
            </button>
          </div>
          <div v-if="googleError" class="field-error">{{ googleError }}</div>
          <div ref="googleResultsEl" class="remote-list">
            <div v-if="googleShowEmptyHint && !googleLoading" class="remote-list-notice">
              <span class="remote-list-notice-icon">i</span>
              <span>Список пуст. Уточните папку или имя.</span>
            </div>
            <template v-if="googleObjects.length">
              <div class="list-toolbar">
                <span class="muted">{{ googleSelectedKeys.length }} выбрано</span>
                <button type="button" class="btn small" @click="googleSelectAll">Все</button>
                <button type="button" class="btn small" @click="googleSelectVideosOnly">Только видео</button>
                <button type="button" class="btn small" @click="googleClearSelection">Сброс</button>
              </div>
              <div class="obj-rows">
                <label v-for="o in googleObjects" :key="o.key" class="obj-row">
                  <input
                    type="checkbox"
                    class="remote-obj-checkbox"
                    :checked="googleSelectedKeys.includes(o.key)"
                    @change="toggleGoogleKey(o.key, ($event.target).checked)"
                  />
                  <span class="obj-key">{{ displayRemoteName(o) }}</span>
                  <span class="obj-size">{{ fmtSize(o.size) }}</span>
                </label>
              </div>
              <button type="button" class="btn primary wide" @click="submitGoogleImport">Импортировать в Linza</button>
            </template>
          </div>
        </template>
      </div>

      <!-- S3 -->
      <div v-show="source === 's3'" class="modal-body">
        <p v-if="profilesLoading" class="muted-inline">Загрузка профилей S3…</p>
        <div v-if="profilesLoadError" class="field-error">{{ profilesLoadError }}</div>

        <div class="s3-mode-row">
          <button
            type="button"
            class="btn small"
            :class="{ active: s3InputMode === 'saved' }"
            :disabled="!sourceProfiles.length"
            @click="onS3ModeChange('saved')"
          >
            Из настроек
          </button>
          <button
            type="button"
            class="btn small"
            :class="{ active: s3InputMode === 'manual' }"
            @click="onS3ModeChange('manual')"
          >
            Вручную
          </button>
        </div>

        <template v-if="s3InputMode === 'saved' && sourceProfiles.length">
          <label class="field-label">Профиль</label>
          <select v-model="selectedProfileId" class="field-input" @change="onProfileSelectChange">
            <option v-for="p in sourceProfiles" :key="p.id" :value="p.id">{{ p.name || p.id }}</option>
          </select>
        </template>

        <template v-if="s3InputMode === 'manual'">
          <label class="field-label">Endpoint</label>
          <input v-model="rEndpoint" type="text" class="field-input" placeholder="https://s3…" />
          <label class="field-label">Bucket</label>
          <input v-model="rBucket" type="text" class="field-input" />
          <label class="field-label">Region</label>
          <input v-model="rRegion" type="text" class="field-input" placeholder="ru-1" />
          <label class="field-label">Access key</label>
          <input v-model="rAccessKey" type="text" class="field-input" autocomplete="off" />
          <label class="field-label">Secret key</label>
          <input v-model="rSecret" type="password" class="field-input" autocomplete="off" />
        </template>

        <label class="field-label">Префикс в бакете</label>
        <input v-model="rPrefix" type="text" class="field-input" placeholder="folder/" />

        <div class="row-actions">
          <button type="button" class="btn primary" :disabled="remoteLoading" @click="fetchRemoteList">
            {{ remoteLoading ? 'Загрузка…' : 'Показать объекты' }}
          </button>
        </div>
        <div v-if="remoteError" class="field-error">{{ remoteError }}</div>

        <div ref="remoteResultsEl" class="remote-list">
          <template v-if="remoteObjects.length">
            <div class="list-toolbar">
              <span class="muted">{{ selectedKeys.length }} выбрано</span>
              <button type="button" class="btn small" @click="selectAll">Все</button>
              <button type="button" class="btn small" @click="selectVideosOnly">Только видео</button>
              <button type="button" class="btn small" @click="clearSelection">Сброс</button>
            </div>
            <div class="obj-rows">
              <label v-for="o in remoteObjects" :key="o.key" class="obj-row">
                <input
                  type="checkbox"
                  class="remote-obj-checkbox"
                  :checked="selectedKeys.includes(o.key)"
                  @change="toggleRemoteKey(o.key, ($event.target).checked)"
                />
                <span class="obj-key">{{ o.key }}</span>
                <span class="obj-size">{{ fmtSize(o.size) }}</span>
              </label>
            </div>
            <button type="button" class="btn primary wide" @click="submitRemoteImport">Импортировать в Linza</button>
          </template>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn ghost" @click="emit('close')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: var(--c-modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5000;
}

.modal {
  background: var(--c-surface, #1e1e2e);
  border: 1px solid var(--c-border, #333);
  border-radius: var(--r-md);
  width: 92%;
  max-width: min(720px, 96vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  color: var(--c-txt, #e8e8ed);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--c-border, #333);
}

.modal-header h2 {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}

.single-mode-hint {
  margin: 0;
  padding: 10px 18px 0;
  font-size: 12px;
  line-height: 1.45;
  color: var(--c-txt-2, #9a9aac);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.35rem;
  cursor: pointer;
  color: var(--c-txt-2, #888);
  line-height: 1;
}
.close-btn:hover {
  color: var(--c-txt, #fff);
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  border-bottom: 1px solid var(--c-border, #333);
  padding: 0 8px;
}

.tab {
  flex: 1 1 auto;
  min-width: 4.5rem;
  padding: 10px 8px;
  border: none;
  background: transparent;
  color: var(--c-txt-2, #888);
  font-size: 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  font-family: inherit;
}

.tab:hover {
  color: var(--c-txt, #e8e8ed);
}

.tab.active {
  color: var(--c-blue, #6b8cff);
  border-bottom-color: var(--c-blue, #6b8cff);
  font-weight: 600;
}

.modal-body {
  padding: 16px 18px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint {
  font-size: 12px;
  color: var(--c-txt-2, #9a9aac);
  margin: 0 0 8px 0;
  line-height: 1.45;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--c-txt-2, #9a9aac);
}

.field-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--c-border, #444);
  border-radius: var(--r-sm);
  background: var(--c-surface-2, #151520);
  color: var(--c-txt, #e8e8ed);
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}

.field-input:focus {
  border-color: var(--c-blue, #6b8cff);
}

.field-error {
  font-size: 12px;
  color: var(--c-err, #f07178);
}

.hidden-input {
  display: none;
}

.row-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.remote-list {
  margin-top: 12px;
  scroll-margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.remote-list-notice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--r-sm);
  font-size: 12px;
  line-height: 1.4;
  background: var(--c-blue-dim, rgba(74, 108, 247, 0.15));
  border: 1px solid rgba(74, 108, 247, 0.35);
  color: var(--c-txt, #e8e8ed);
}

.remote-list-notice-icon {
  flex-shrink: 0;
  font-weight: 700;
  opacity: 0.9;
}

.list-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.muted {
  font-size: 11px;
  color: var(--c-txt-2, #888);
  margin-right: auto;
}

.obj-rows {
  max-height: 220px;
  overflow-y: auto;
  border: 1px solid var(--c-border, #333);
  border-radius: var(--r-sm);
  background: var(--c-surface-2, #151520);
}

.obj-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--c-border, #2a2a38);
  font-size: 11px;
  cursor: pointer;
}

.obj-row:last-child {
  border-bottom: none;
}

.remote-obj-checkbox {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  margin-top: 2px;
  accent-color: var(--c-blue, #2563eb);
  cursor: pointer;
}

.obj-key {
  flex: 1;
  word-break: break-all;
  color: var(--c-txt, #e8e8ed);
}

.obj-size {
  flex-shrink: 0;
  color: var(--c-txt-2, #888);
  white-space: nowrap;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 18px;
  border-top: 1px solid var(--c-border, #333);
}

.btn {
  padding: 7px 16px;
  border-radius: var(--r-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  font-family: inherit;
}

.btn.primary {
  background: var(--c-blue, #4a6cf7);
  color: #fff;
}

.btn.primary:hover:not(:disabled) {
  background: var(--c-blue-hover, #3d5ed4);
}

.btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.ghost {
  background: transparent;
  border-color: var(--c-border, #444);
  color: var(--c-txt-2, #aaa);
}

.btn.ghost:hover {
  background: var(--c-surface-2, #252530);
}

.s3-mode-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 12px;
}

.btn.small {
  padding: 4px 10px;
  font-size: 11px;
  background: var(--c-surface-2, #252530);
  border: 1px solid var(--c-border, #444);
  color: var(--c-txt, #ddd);
}

.btn.small.active {
  border-color: var(--c-blue, #4a6cf7);
  color: var(--c-blue, #7b93fc);
  background: rgba(74, 108, 247, 0.12);
}

.btn.small:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.muted-inline {
  font-size: 12px;
  color: var(--c-txt-2, #888);
  margin: 0 0 8px;
}

.btn.wide {
  width: 100%;
  margin-top: 4px;
}

.yandex-connected-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.btn-link {
  background: none;
  border: none;
  padding: 0;
  font-size: 11px;
  cursor: pointer;
  font-family: inherit;
  color: var(--c-blue, #6b8cff);
  text-decoration: underline;
}

.btn-link.danger {
  color: var(--c-err, #f07178);
}
</style>
