<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NAlert,
  NButton,
  NCard,
  NCheckbox,
  NEmpty,
  NIcon,
  NInput,
  NModal,
  NPagination,
  NProgress,
  NSpace,
  NSpin,
  NTag,
  NDivider,
  useDialog,
} from 'naive-ui'
import {
  AddOutline,
  RefreshOutline,
  PlayOutline,
  TrashOutline,
  ListOutline,
  CloudUploadOutline,
} from '@vicons/ionicons5'
import AddFilesModal from '../components/AddFilesModal.vue'
import SourcesPage from './SourcesPage.vue'
import { useAuth } from '../composables/useAuth.js'

const route = useRoute()
const router = useRouter()

const { getToken, fetchMe, canAccessSettings } = useAuth()
const dialog = useDialog()

const UPLOAD_PREFIX = 'uploads/'
const SOURCE_PREFIX = 'sources/'

const showModal = ref(false)
/** Вкладка модалки «Добавить» (после OAuth — yandex / google). */
const addFilesInitialSource = ref('file')
/** Сброс модалки при OAuth-редиректе, чтобы гарантированно вызвались load* статуса. */
const addFilesModalKey = ref(0)
/** Явная перезагрузка статуса OAuth во вкладках модалки (после редиректа с провайдера). */
const addFilesModalRef = ref(null)
/** Список «Подключённые источники» на странице — обновить OAuth после редиректа/отключения в модалке */
const sourcesPageRef = ref(null)
/** Полный S3-ключ — открыт проигрыватель; пустая строка = закрыто */
const previewStorageKey = ref('')
const uploadFiles = ref([])
const sourceFiles = ref([])
const tasks = ref([])
const loadError = ref('')
const queueError = ref('')
/** Сообщение после редиректа с Яндекс OAuth */
const yandexNotice = ref('')
/** Сообщение после редиректа с Google OAuth */
const googleNotice = ref('')
const eventSources = ref({})

const queueItems = ref([])
/** Полные S3-ключи (uploads/… и sources/…) — один список выбора */
const selectedStorageKeys = ref([])
const queueBusy = ref(false)
const deleteBusy = ref(false)

/** Первый запрос к /api/files — показываем плейсхолдер, пока S3 отдаёт длинный список */
const filesLoading = ref(true)
const pageSize = ref(20)
const currentPage = ref(1)
const fileSearch = ref('')
const refreshBusy = ref(false)

const VIDEO_EXT_RE = /\.(mp4|webm|mov|avi|mkv)$/i

function queryFlagOne(q, key) {
  const v = q?.[key]
  if (v == null || v === '') return false
  if (Array.isArray(v)) return v.some((x) => String(x) === '1')
  return String(v) === '1'
}

function firstQueryString(q, key) {
  const v = q?.[key]
  if (v == null || v === '') return ''
  if (Array.isArray(v)) return String(v[0] ?? '')
  return String(v)
}

/** Базовый URL очереди (со слэшем — совпадает с регистрацией маршрутов FastAPI). */
const ANALYSIS_QUEUE_URL = '/api/analysis-queue/'

function authHeaders(json = true) {
  const h = { Authorization: `Bearer ${getToken()}` }
  if (json) h['Content-Type'] = 'application/json'
  return h
}

function displayName(storageKey) {
  if (!storageKey) return ''
  return storageKey.replace(new RegExp(`^(${UPLOAD_PREFIX}|${SOURCE_PREFIX})`), '')
}

function isVideoStorageKey(storageKey) {
  return storageKey && VIDEO_EXT_RE.test(displayName(storageKey))
}

/** Путь для GET /api/files/download/… (сегменты закодированы) */
function downloadUrlForKey(storageKey) {
  if (!storageKey) return ''
  return `/api/files/download/${storageKey.split('/').map(encodeURIComponent).join('/')}`
}

function openVideoPreview(storageKey) {
  if (!storageKey || !isVideoStorageKey(storageKey)) return
  previewStorageKey.value = storageKey
}

function closeVideoPreview() {
  previewStorageKey.value = ''
}

function onPreviewEscape(e) {
  if (e.key === 'Escape') closeVideoPreview()
}

function isUploadKey(key) {
  return key && (key.startsWith(UPLOAD_PREFIX) || !key.startsWith(SOURCE_PREFIX))
}

function isSourceKey(key) {
  return key && key.startsWith(SOURCE_PREFIX)
}

function taskInUploads(t) {
  return isUploadKey(t.filename)
}

function taskInSources(t) {
  return isSourceKey(t.filename)
}

function fileRowsForList(files, prefixFilter) {
  return files
    .filter(f => {
      if (prefixFilter === 'upload') return isUploadKey(f.name)
      return isSourceKey(f.name)
    })
    .map(f => ({
      key: 'file:' + f.name,
      name: f.name,
      display: displayName(f.name),
      size: f.size,
      lastModified: f.last_modified,
      status: 'completed',
      progress: f.size,
      total: f.size,
      error: null,
    }))
}

function taskRowsForList(prefixFilter) {
  return tasks.value
    .filter(t => (prefixFilter === 'upload' ? taskInUploads(t) : taskInSources(t)))
    .map(t => ({
      key: 'task:' + t.task_id,
      name: t.filename,
      display: displayName(t.filename),
      size: t.total || null,
      lastModified: null,
      status: t.status,
      progress: t.progress || 0,
      total: t.total || 0,
      error: t.error || null,
      batch_index: t.batch_index,
      batch_total: t.batch_total,
    }))
}

const uploadRows = computed(() => {
  const busy = new Set(tasks.value.filter(taskInUploads).map(t => t.filename))
  const tr = taskRowsForList('upload')
  const fr = fileRowsForList(uploadFiles.value, 'upload').filter(r => !busy.has(r.name))
  return [...tr, ...fr]
})

const sourceRows = computed(() => {
  const busy = new Set(tasks.value.filter(taskInSources).map(t => t.filename))
  const tr = taskRowsForList('sources')
  const fr = fileRowsForList(sourceFiles.value, 'sources').filter(r => !busy.has(r.name))
  return [...tr, ...fr]
})

/** Одна таблица: загрузки и импорт с внешнего S3 в одном хранилище */
const storageRows = computed(() => [...uploadRows.value, ...sourceRows.value])

const filteredStorageRows = computed(() => {
  const q = fileSearch.value.trim().toLowerCase()
  const rows = storageRows.value
  if (!q) return rows
  return rows.filter((r) => (r.display || r.name || '').toLowerCase().includes(q))
})

const totalStorageRows = computed(() => filteredStorageRows.value.length)

const paginatedStorageRows = computed(() => {
  const rows = filteredStorageRows.value
  const start = (currentPage.value - 1) * pageSize.value
  return rows.slice(start, start + pageSize.value)
})

watch(fileSearch, () => {
  currentPage.value = 1
})

watch([totalStorageRows, pageSize], () => {
  const tp = Math.max(1, Math.ceil(totalStorageRows.value / pageSize.value) || 1)
  if (currentPage.value > tp) currentPage.value = tp
})

watch(previewStorageKey, (key) => {
  if (key) window.addEventListener('keydown', onPreviewEscape)
  else window.removeEventListener('keydown', onPreviewEscape)
})

/** Блокируем повторное добавление пока задача ждёт или крутится на детекторе */
const queuedKeySet = computed(() => {
  const active = queueItems.value.filter((q) => q.status === 'pending' || q.status === 'processing')
  return new Set(active.map((q) => q.storage_key))
})

/** Сколько задач ещё ждут или обрабатываются — для компактной полосы на странице файлов. */
const queueActiveCount = computed(
  () => queueItems.value.filter((q) => q.status === 'pending' || q.status === 'processing').length,
)

let queuePollTimer = null
function syncQueuePolling() {
  const active = queueItems.value.some((q) => q.status === 'pending' || q.status === 'processing')
  if (active && !queuePollTimer) {
    queuePollTimer = setInterval(loadQueue, 4000)
  } else if (!active && queuePollTimer) {
    clearInterval(queuePollTimer)
    queuePollTimer = null
  }
}

watch(pageSize, () => {
  currentPage.value = 1
})

function fmtSize(bytes) {
  if (bytes == null) return '—'
  if (bytes === 0) return '0 Б'
  const units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function progressPercent(row) {
  if (!row.total) return 0
  return Math.round((row.progress / row.total) * 100)
}

function statusLabel(row) {
  if (row.status === 'completed') return '✓ Готово'
  if (row.status === 'error') return '✗ Ошибка'
  const batch =
    row.batch_total > 1 && row.batch_index
      ? `${row.batch_index}/${row.batch_total} · `
      : ''
  if (row.status === 'downloading_from_remote') return `${batch}Чтение из внешнего S3…`
  if (row.status === 'downloading') return `${batch}Скачивание…`
  if (row.status === 'uploading') return `${batch}Загрузка в хранилище…`
  return 'Ожидание…'
}

/**
 * @param {{ silent?: boolean }} options — silent: не показывать полноэкранный лоадер (обновление после задачи)
 */
async function loadFiles(options = {}) {
  const silent = options.silent === true
  if (!silent) {
    filesLoading.value = true
    loadError.value = ''
  }
  try {
    const res = await fetch('/api/files')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (Array.isArray(data.uploads) || Array.isArray(data.from_sources)) {
      uploadFiles.value = data.uploads || []
      sourceFiles.value = data.from_sources || []
    } else if (Array.isArray(data.files)) {
      uploadFiles.value = data.files.filter(f => isUploadKey(f.name))
      sourceFiles.value = data.files.filter(f => isSourceKey(f.name))
    } else {
      uploadFiles.value = []
      sourceFiles.value = []
    }
    for (const t of data.tasks || []) {
      if (!tasks.value.find(x => x.task_id === t.task_id)) {
        tasks.value.push(t)
        startSSE(t.task_id)
      }
    }
  } catch (e) {
    loadError.value = 'Ошибка загрузки списка файлов: ' + e.message
  } finally {
    if (!silent) filesLoading.value = false
  }
}

async function loadQueue() {
  queueError.value = ''
  try {
    const res = await fetch(ANALYSIS_QUEUE_URL, { headers: authHeaders(false) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    queueItems.value = await res.json()
    syncQueuePolling()
  } catch (e) {
    queueError.value = 'Не удалось загрузить очередь: ' + e.message
  }
}

async function addQueueKeys(keys) {
  if (!keys.length) return
  queueBusy.value = true
  queueError.value = ''
  try {
    const res = await fetch(ANALYSIS_QUEUE_URL, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ storage_keys: keys }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    selectedStorageKeys.value = []
    await loadQueue()
  } catch (e) {
    queueError.value = e.message
  } finally {
    queueBusy.value = false
  }
}

function toggleSelectStorage(storageKey, checked) {
  const cur = selectedStorageKeys.value
  if (checked && !cur.includes(storageKey)) {
    selectedStorageKeys.value = [...cur, storageKey]
  } else if (!checked && cur.includes(storageKey)) {
    selectedStorageKeys.value = cur.filter((k) => k !== storageKey)
  }
}

async function deleteKeysFromStorage(keys) {
  if (!keys.length || deleteBusy.value) return
  deleteBusy.value = true
  loadError.value = ''
  try {
    const res = await fetch('/api/files/delete-objects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keys }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const msg = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg || d).join('; ')
        : data.detail
      throw new Error(msg || `HTTP ${res.status}`)
    }
    if (data.errors?.length) {
      loadError.value =
        'Часть файлов не удалена: ' + data.errors.map((e) => `${e.key}: ${e.error}`).join('; ')
    }
    selectedStorageKeys.value = selectedStorageKeys.value.filter((k) => !keys.includes(k))
    await loadFiles({ silent: true })
    await loadQueue()
  } catch (e) {
    loadError.value = 'Удаление: ' + e.message
  } finally {
    deleteBusy.value = false
  }
}

function requestDeleteSelected() {
  const keys = [...selectedStorageKeys.value]
  if (!keys.length || deleteBusy.value) return
  dialog.warning({
    title: 'Удалить из хранилища?',
    content:
      `Безвозвратно удалить ${keys.length} объект(ов)? При необходимости уберите связанные записи из очереди анализа вручную.`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: () => deleteKeysFromStorage(keys),
  })
}

async function refreshLists() {
  refreshBusy.value = true
  try {
    await Promise.all([loadFiles({ silent: true }), loadQueue()])
  } finally {
    refreshBusy.value = false
  }
}

function pushTask(task_id, filename, extra = {}) {
  tasks.value.push({
    task_id,
    filename,
    status: 'pending',
    progress: 0,
    total: 0,
    ...extra,
  })
  startSSE(task_id)
}

async function handleUploadUrl(url) {
  closeAddFilesModal()
  try {
    const res = await fetch('/api/files/upload-from-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const { task_id, filename } = await res.json()
    pushTask(task_id, filename)
  } catch (e) {
    loadError.value = 'Не удалось начать загрузку: ' + e.message
  }
}

async function handleUploadFile(file) {
  closeAddFilesModal()
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await fetch('/api/files/upload-local', { method: 'POST', body: fd })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const { task_id, filename } = await res.json()
    pushTask(task_id, filename)
  } catch (e) {
    loadError.value = 'Не удалось загрузить файл: ' + e.message
  }
}

async function handleImportYandexMe(body) {
  closeAddFilesModal()
  try {
    const res = await fetch('/api/integrations/yandex/files/import', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ keys: body.keys }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      const msg = Array.isArray(err.detail)
        ? err.detail.map(d => d.msg).join('; ')
        : err.detail
      throw new Error(msg || `HTTP ${res.status}`)
    }
    const { task_id, keys } = await res.json()
    pushTask(task_id, keys[0], { batch_index: 1, batch_total: keys.length })
  } catch (e) {
    loadError.value = 'Импорт с Яндекс.Диска не запустился: ' + e.message
  }
}

async function handleImportGoogleMe(body) {
  closeAddFilesModal()
  const n = body.keys?.length || 0
  try {
    const res = await fetch('/api/integrations/google/files/import', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ keys: body.keys }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      const msg = Array.isArray(err.detail)
        ? err.detail.map(d => d.msg).join('; ')
        : err.detail
      throw new Error(msg || `HTTP ${res.status}`)
    }
    const { task_id, keys } = await res.json()
    pushTask(task_id, keys[0], { batch_index: 1, batch_total: n || keys.length })
  } catch (e) {
    loadError.value = 'Импорт с Google Диска не запустился: ' + e.message
  }
}

async function handleImportS3(body) {
  closeAddFilesModal()
  const byProfile = body.profile_id != null && body.profile_id !== ''
  const url = byProfile ? '/api/files/remote-s3/import-by-profile' : '/api/files/remote-s3/import'
  const payload = byProfile
    ? { profile_id: body.profile_id, keys: body.keys }
    : body
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      const msg = Array.isArray(err.detail)
        ? err.detail.map(d => d.msg).join('; ')
        : err.detail
      throw new Error(msg || `HTTP ${res.status}`)
    }
    const { task_id, keys } = await res.json()
    pushTask(task_id, keys[0], { batch_index: 1, batch_total: keys.length })
  } catch (e) {
    loadError.value = 'Импорт из облака не запустился: ' + e.message
  }
}

function startSSE(task_id) {
  if (eventSources.value[task_id]) return
  const es = new EventSource(`/api/files/progress/${task_id}`)
  eventSources.value[task_id] = es

  es.onmessage = (event) => {
    const data = JSON.parse(event.data)
    const idx = tasks.value.findIndex(t => t.task_id === task_id)
    if (idx !== -1) {
      tasks.value[idx] = { ...tasks.value[idx], ...data }
    }
    if (data.status === 'completed') {
      es.close()
      delete eventSources.value[task_id]
      setTimeout(() => {
        tasks.value = tasks.value.filter(t => t.task_id !== task_id)
        loadFiles({ silent: true })
      }, 1500)
    } else if (data.status === 'error') {
      es.close()
      delete eventSources.value[task_id]
    }
  }

  es.onerror = () => {
    es.close()
    delete eventSources.value[task_id]
  }
}

function openAddFilesModal(tab = 'file') {
  addFilesInitialSource.value = tab
  if (tab === 'yandex' || tab === 'google') {
    addFilesModalKey.value += 1
  }
  showModal.value = true
}

function closeAddFilesModal() {
  showModal.value = false
  addFilesInitialSource.value = 'file'
}

function onCloudIntegrationsChanged() {
  sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
}

onMounted(async () => {
  await fetchMe()
  if (queryFlagOne(route.query, 'yandex_connected')) {
    yandexNotice.value =
      'Яндекс.Диск подключён. Открыто окно импорта на вкладке «Яндекс» — выберите файлы или нажмите «Показать файлы».'
    openAddFilesModal('yandex')
    await nextTick()
    await addFilesModalRef.value?.reloadYandexConnection?.()
    sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
    router.replace({ path: route.path, query: {} })
    await nextTick()
    await addFilesModalRef.value?.reloadYandexConnection?.()
    sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
  } else if (firstQueryString(route.query, 'yandex_error')) {
    yandexNotice.value = 'Яндекс: ' + firstQueryString(route.query, 'yandex_error')
    router.replace({ path: route.path, query: {} })
  } else if (queryFlagOne(route.query, 'google_connected')) {
    googleNotice.value =
      'Google Диск подключён. Открыто окно импорта — вкладка «Google»; нажмите «Показать файлы» и выберите материалы.'
    openAddFilesModal('google')
    await nextTick()
    await addFilesModalRef.value?.reloadGoogleConnection?.()
    sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
    router.replace({ path: route.path, query: {} })
    await nextTick()
    await addFilesModalRef.value?.reloadGoogleConnection?.()
    sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
    setTimeout(() => {
      addFilesModalRef.value?.reloadGoogleConnection?.()
      sourcesPageRef.value?.refreshOauthIntegrationStatus?.()
    }, 400)
  } else if (firstQueryString(route.query, 'google_error')) {
    googleNotice.value = 'Google: ' + firstQueryString(route.query, 'google_error')
    router.replace({ path: route.path, query: {} })
  }
  loadFiles()
  loadQueue()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onPreviewEscape)
  Object.values(eventSources.value).forEach(es => es.close())
  if (queuePollTimer) {
    clearInterval(queuePollTimer)
    queuePollTimer = null
  }
})
</script>

<template>
  <div class="files-page">
    <SourcesPage v-if="canAccessSettings()" ref="sourcesPageRef" embedded />

    <div class="files-stack">
      <NAlert v-if="loadError" type="error" :bordered="false" closable @close="loadError = ''">
        {{ loadError }}
      </NAlert>
      <NAlert v-if="queueError" type="warning" :bordered="false" closable @close="queueError = ''">
        {{ queueError }}
      </NAlert>
      <NAlert
        v-if="yandexNotice"
        type="success"
        :bordered="false"
        closable
        class="notice-alert"
        @close="yandexNotice = ''"
      >
        {{ yandexNotice }}
      </NAlert>
      <NAlert
        v-if="googleNotice"
        type="info"
        :bordered="false"
        closable
        class="notice-alert"
        @close="googleNotice = ''"
      >
        {{ googleNotice }}
      </NAlert>
    </div>

    <header class="hdr">
      <div class="hdr-main">
        <div class="hdr-txt">
          <h1 class="pg-t">
            <NIcon :component="CloudUploadOutline" class="hdr-ic" />
            Загруженные файлы
          </h1>
          <p class="pg-d">
            Загрузка и хранение видео. Отправка в анализ — кнопкой ниже; статусы обработки смотрите в разделе «Очередь анализа».
          </p>
        </div>
        <NSpace v-if="storageRows.length" class="hdr-chips" :size="8" align="center" wrap>
          <NTag round :bordered="false" size="small" type="default">
            {{ storageRows.length }} в хранилище
          </NTag>
        </NSpace>
      </div>
      <NSpace class="hdr-actions" :size="10" wrap align="center">
        <NButton type="primary" @click="openAddFilesModal('file')">
          <template #icon><NIcon :component="AddOutline" /></template>
          Добавить
        </NButton>
        <NButton quaternary :loading="refreshBusy" :disabled="filesLoading" @click="refreshLists">
          <template #icon><NIcon :component="RefreshOutline" /></template>
          Обновить
        </NButton>
        <template v-if="selectedStorageKeys.length">
          <NDivider vertical class="hdr-divider" />
          <NTag type="primary" size="small" round :bordered="false">
            Выбрано: {{ selectedStorageKeys.length }}
          </NTag>
          <NButton type="primary" secondary :disabled="queueBusy" @click="addQueueKeys([...selectedStorageKeys])">
            <template #icon><NIcon :component="ListOutline" /></template>
            В очередь на анализ
          </NButton>
          <NButton type="error" ghost :disabled="deleteBusy" @click="requestDeleteSelected">
            <template #icon><NIcon :component="TrashOutline" /></template>
            Удалить
          </NButton>
        </template>
      </NSpace>
    </header>

    <div class="queue-strip" :class="{ 'queue-strip--active': queueItems.length > 0 }">
      <div class="queue-strip-main">
        <NIcon :component="ListOutline" class="queue-strip-ic" />
        <div class="queue-strip-txt">
          <template v-if="queueItems.length">
            <span class="queue-strip-lead">
              <strong>{{ queueItems.length }}</strong> в очереди на анализ
            </span>
            <span v-if="queueActiveCount" class="queue-strip-sub">
              {{ queueActiveCount }} в ожидании или в работе
            </span>
          </template>
          <template v-else>
            <span class="queue-strip-lead">Очередь анализа пуста</span>
            <span class="queue-strip-sub">Выберите готовые файлы и нажмите «В очередь на анализ»</span>
          </template>
        </div>
      </div>
      <NButton type="primary" secondary size="small" @click="router.push('/operator/queue')">
        {{ queueItems.length ? 'Открыть очередь' : 'Перейти к очереди' }}
      </NButton>
    </div>

    <NCard class="files-card" :bordered="true" size="small" :segmented="{ content: true }">
      <template #header>
        <div class="card-head-inner">
          <span class="card-head-title">Файлы</span>
          <NInput
            v-model:value="fileSearch"
            clearable
            placeholder="Поиск по имени…"
            class="file-search"
            :disabled="filesLoading"
          />
        </div>
      </template>

      <NSpin :show="filesLoading" :description="'Загрузка списка…'">
        <div class="table-shell">
          <table class="files-table">
            <thead>
              <tr>
                <th class="th-check" aria-label="Выбор" />
                <th>Файл</th>
                <th class="th-num">Размер</th>
                <th class="th-prog">Статус</th>
                <th class="th-date">Изменён</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!filesLoading && paginatedStorageRows.length === 0">
                <td colspan="5" class="empty-cell">
                  <NEmpty
                    :description="
                      storageRows.length === 0
                        ? 'Нет файлов. Нажмите «Добавить» — с устройства, по ссылке или из облака.'
                        : 'Ничего не найдено по запросу'
                    "
                  />
                </td>
              </tr>
              <tr
                v-for="row in paginatedStorageRows"
                :key="row.key"
                :class="{
                  'row-error': row.status === 'error',
                  'row-queued': row.status === 'completed' && queuedKeySet.has(row.name),
                }"
              >
                <td class="cell-check">
                  <NCheckbox
                    v-if="row.status === 'completed'"
                    :checked="queuedKeySet.has(row.name) || selectedStorageKeys.includes(row.name)"
                    :disabled="queuedKeySet.has(row.name)"
                    @update:checked="(v) => toggleSelectStorage(row.name, v)"
                  />
                </td>
                <td class="cell-name">
                  <div class="file-name-row">
                    <video
                      v-if="row.status === 'completed' && isVideoStorageKey(row.name)"
                      class="file-thumb file-thumb-clickable"
                      :src="downloadUrlForKey(row.name)"
                      preload="metadata"
                      muted
                      playsinline
                      title="Открыть просмотр"
                      @click.prevent.stop="openVideoPreview(row.name)"
                    />
                    <div v-else-if="isVideoStorageKey(row.name)" class="file-thumb file-thumb-skeleton" aria-hidden="true">
                      <span class="thumb-spinner" />
                    </div>
                    <div class="file-name-text">
                      <span class="filename">{{ row.display || row.name }}</span>
                      <NSpace :size="6" wrap align="center">
                        <NTag v-if="queuedKeySet.has(row.name)" size="tiny" round type="info" :bordered="false">
                          в очереди
                        </NTag>
                        <NButton
                          v-if="row.status === 'completed' && isVideoStorageKey(row.name)"
                          text
                          type="primary"
                          size="tiny"
                          @click.stop="openVideoPreview(row.name)"
                        >
                          <template #icon><NIcon :component="PlayOutline" :size="14" /></template>
                          Просмотр
                        </NButton>
                      </NSpace>
                    </div>
                  </div>
                </td>
                <td class="cell-size">{{ fmtSize(row.size) }}</td>
                <td class="cell-progress">
                  <template v-if="row.status === 'completed'">
                    <NTag type="success" size="small" round :bordered="false">Готово</NTag>
                  </template>
                  <template v-else-if="row.status === 'error'">
                    <NTag type="error" size="small" round :bordered="false" :title="row.error || ''">
                      Ошибка
                    </NTag>
                  </template>
                  <template v-else>
                    <div class="prog-block">
                      <NProgress
                        type="line"
                        :percentage="progressPercent(row)"
                        :indicator-placement="'inside'"
                        processing
                        :height="10"
                        :border-radius="6"
                      />
                      <span class="prog-caption">{{ statusLabel(row) }}</span>
                    </div>
                  </template>
                </td>
                <td class="cell-date">{{ fmtDate(row.lastModified) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalStorageRows > 0" class="files-footer">
          <span class="footer-range">
            {{ Math.min((currentPage - 1) * pageSize + 1, totalStorageRows) }}–{{
              Math.min(currentPage * pageSize, totalStorageRows)
            }}
            из {{ totalStorageRows }}
          </span>
          <NPagination
            v-model:page="currentPage"
            v-model:page-size="pageSize"
            :item-count="totalStorageRows"
            :page-sizes="[10, 20, 50, 100]"
            show-size-picker
          />
        </div>
      </NSpin>
    </NCard>

    <NModal
      :show="!!previewStorageKey"
      preset="card"
      :title="previewStorageKey ? displayName(previewStorageKey) : ''"
      class="video-modal"
      :style="{ width: 'min(920px, 96vw)' }"
      :bordered="false"
      @update:show="(v) => !v && closeVideoPreview()"
    >
      <video
        v-if="previewStorageKey"
        :key="previewStorageKey"
        class="video-preview-player"
        controls
        playsinline
        preload="metadata"
        :src="downloadUrlForKey(previewStorageKey)"
      />
    </NModal>

    <Transition name="linza-modal">
      <AddFilesModal
        v-if="showModal"
        ref="addFilesModalRef"
        :key="addFilesModalKey"
        :initial-source="addFilesInitialSource"
        @close="closeAddFilesModal"
        @upload-url="handleUploadUrl"
        @upload-file="handleUploadFile"
        @import-s3="handleImportS3"
        @import-yandex-me="handleImportYandexMe"
        @import-google-me="handleImportGoogleMe"
        @cloud-integrations-changed="onCloudIntegrationsChanged"
      />
    </Transition>
  </div>
</template>

<style scoped>
.files-page {
  max-width: 1120px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.files-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notice-alert {
  border-radius: var(--r-md);
}

.hdr {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hdr-main {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.hdr-txt {
  min-width: 0;
  flex: 1;
}

.pg-t {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 8px;
  color: var(--c-txt);
}

.hdr-ic {
  flex-shrink: 0;
  color: var(--c-blue);
}

.pg-d {
  font-size: 14px;
  line-height: 1.5;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 56ch;
}

.hdr-chips {
  flex-shrink: 0;
  padding-top: 4px;
}

.hdr-actions {
  flex-wrap: wrap;
}

.hdr-divider {
  height: 28px;
  margin: 0 4px;
}

.files-card :deep(.n-card-header) {
  padding-bottom: 12px;
}

.card-head-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.card-head-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--c-txt);
}

.file-search {
  width: min(100%, 280px);
}

.table-shell {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: var(--r-sm);
}

.files-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  font-size: 13px;
}

.files-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--c-txt-2);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface-2);
}

.th-check {
  width: 44px;
  text-align: center;
}

.th-num {
  width: 88px;
}

.th-prog {
  min-width: 160px;
  width: 22%;
}

.th-date {
  width: 130px;
}

.files-table td {
  padding: 12px;
  border-bottom: 1px solid var(--c-border);
  vertical-align: middle;
}

.files-table tbody tr:hover td {
  background: var(--c-row-hover);
}

.row-error td {
  background: var(--c-err-bg);
}

.row-queued td {
  opacity: 0.92;
}

.cell-check {
  text-align: center;
}

.empty-cell {
  padding: 36px 16px !important;
  border-bottom: none !important;
}

.file-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.file-thumb {
  flex-shrink: 0;
  width: 80px;
  height: 52px;
  object-fit: cover;
  border-radius: var(--r-md);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
}

.file-thumb-clickable {
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.file-thumb-clickable:hover {
  border-color: var(--c-blue);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.25);
}

.file-thumb-skeleton {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(
    110deg,
    var(--c-surface-2) 0%,
    var(--c-surface-2) 40%,
    var(--c-border) 50%,
    var(--c-surface-2) 60%,
    var(--c-surface-2) 100%
  );
  background-size: 200% 100%;
  animation: thumb-shimmer 1.3s ease-in-out infinite;
}

.thumb-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid var(--c-border);
  border-top-color: var(--c-blue);
  border-radius: 50%;
  animation: spin-360 0.65s linear infinite;
}

@keyframes thumb-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

@keyframes spin-360 {
  to {
    transform: rotate(360deg);
  }
}

.file-name-text {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.filename {
  word-break: break-all;
  color: var(--c-txt);
  font-weight: 500;
}

.cell-size {
  white-space: nowrap;
  color: var(--c-txt-2);
  font-variant-numeric: tabular-nums;
}

.cell-date {
  white-space: nowrap;
  color: var(--c-txt-3);
  font-size: 12px;
}

.prog-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  max-width: 240px;
}

.prog-caption {
  font-size: 11px;
  color: var(--c-txt-3);
  line-height: 1.35;
}

.files-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--c-border);
}

.footer-range {
  font-size: 12px;
  color: var(--c-txt-3);
  font-variant-numeric: tabular-nums;
}

.queue-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px 16px;
  padding: 14px 16px;
  margin-bottom: 18px;
  border-radius: var(--r-lg);
  border: 1px solid var(--c-border);
  background: var(--c-surface-2);
}

.queue-strip--active {
  border-color: rgba(59, 130, 246, 0.35);
  background: var(--c-blue-dim);
}

.queue-strip-main {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.queue-strip-ic {
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 20px;
  color: var(--c-blue);
}

.queue-strip-txt {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.queue-strip-lead {
  font-size: 14px;
  color: var(--c-txt);
  line-height: 1.35;
}

.queue-strip-sub {
  font-size: 12px;
  color: var(--c-txt-3);
  line-height: 1.4;
}

.video-preview-player {
  display: block;
  width: 100%;
  max-height: min(72vh, 640px);
  border-radius: var(--r-lg);
  background: #0a0a0a;
}

@media (max-width: 640px) {
  .hdr-main {
    flex-direction: column;
  }

  .queue-strip {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
