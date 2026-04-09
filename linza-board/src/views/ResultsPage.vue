<script setup>
import { ref, h, onMounted, computed, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NTag,
  NCard,
  NSpace,
  NEmpty,
  NSpin,
  NAlert,
  NIcon,
  NPopconfirm,
  NSelect,
  NTooltip,
  useMessage,
} from 'naive-ui'
import { PlayOutline, TrashOutline, CheckmarkDoneOutline, ScaleOutline } from '@vicons/ionicons5'
import { useReports } from '../composables/useReports.js'
import { extractAndNormalize } from '../composables/detectionsPayload.js'
import { useAuth } from '../composables/useAuth.js'
import VideoPlayer from '../components/VideoPlayer.vue'
import { extractVafJobId } from '../utils/vafJobId.js'

const route = useRoute()
const router = useRouter()
const { hasPortalRole, activePortalRole } = useAuth()
const showQueueCta = computed(() => hasPortalRole('operator'))
const message = useMessage()
const { reports, loading, fetchReports, deleteReport, getReport, patchReport } = useReports()

/** Виртуальный скролл при большом числе строк — меньше DOM, плавнее скролл. */
const TABLE_V_SCROLL_MIN = 32
const tableMaxHeight = 560
const useVirtualTable = computed(() => reports.value.length >= TABLE_V_SCROLL_MIN)

/** Строки с активным PATCH — для блокировки контролов и спиннеров. */
const patching = shallowRef(new Set())
function patchStart(id) {
  const n = new Set(patching.value)
  n.add(id)
  patching.value = n
}
function patchEnd(id) {
  const n = new Set(patching.value)
  n.delete(id)
  patching.value = n
}
function isPatching(id) {
  return patching.value.has(id)
}

/** Оператор не меняет маркировку после своей ревизии или пока отчёт у юриста (сервер тоже режет PATCH). */
function canEditMarking(row) {
  if (isPatching(row.id)) return false
  const ar = activePortalRole()
  if (ar === 'operator' && (row.revision_done || row.escalated)) return false
  return true
}

const MARKING_OPTIONS = [
  { label: 'Не задана', value: null },
  { label: 'Чисто (0+)', value: 'clean' },
  { label: '12+', value: 'age_12' },
  { label: '16+', value: 'age_16' },
  { label: '18+', value: 'age_18' },
  { label: 'Запрещено', value: 'banned' },
]

const showPlayer = ref(false)
const playerFilename = ref('')
const playerDetections = ref([])
const playerTitle = ref('')
const playerReportLabel = ref('')
const playerViolationsCount = ref(null)
const playerVafJobId = ref('')

function statusType(status) {
  if (status === 'success') return 'success'
  if (status === 'error') return 'error'
  return 'warning'
}

function statusLabel(status) {
  if (status === 'success') return 'Успех'
  if (status === 'error') return 'Ошибка'
  return 'Обработка'
}

async function openPlayer(report) {
  playerTitle.value = report.filename
  playerReportLabel.value = `Отчёт #${report.id}`
  let list = []
  playerVafJobId.value = ''
  try {
    const full = await getReport(report.id)
    const raw = full.report_json
    if (raw != null && String(raw).trim() !== '') {
      let j = typeof raw === 'string' ? JSON.parse(raw) : raw
      if (typeof j === 'string') {
        try {
          j = JSON.parse(j)
        } catch {
          /* одна строка в БД */
        }
      }
      list = extractAndNormalize(j).list
      playerVafJobId.value = extractVafJobId(j)
    }
  } catch (e) {
    console.warn('[ResultsPage] report_json / детекции:', e)
    list = []
  }
  playerViolationsCount.value = list.length
  playerFilename.value = report.filename
  playerDetections.value = list
  showPlayer.value = true
}

async function consumeReportIdFromQuery() {
  const raw = route.query.reportId
  if (raw == null || raw === '') return
  const id = Number(Array.isArray(raw) ? raw[0] : String(raw))
  const q = { ...route.query }
  delete q.reportId
  if (Number.isNaN(id)) {
    router.replace({ path: '/results', query: q })
    return
  }
  const row = reports.value.find((x) => x.id === id)
  if (row) await openPlayer(row)
  router.replace({ path: '/results', query: q })
}

async function handleDelete(id) {
  try {
    await deleteReport(id)
  } catch (e) {
    alert(e.message)
  }
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('ru-RU')
}

/** Эвристика, если в БД ещё нет content_marking. */
function aiVerdict(row) {
  if (row.status !== 'success') return { text: '—', type: 'default' }
  const n = Number(row.match_count ?? 0)
  if (n === 0) return { text: '✓ Чисто', type: 'success' }
  if (n >= 25) return { text: '⛔ Запрещено', type: 'error' }
  if (n >= 12) return { text: '⚠ 18+', type: 'warning' }
  if (n >= 4) return { text: '⚠ 16+', type: 'info' }
  return { text: '⚠ 16+', type: 'warning' }
}

function verdictFromMarking(m) {
  if (!m) return null
  const map = {
    clean: { text: '✓ Чисто', type: 'success' },
    age_12: { text: '12+', type: 'info' },
    age_16: { text: '16+', type: 'warning' },
    age_18: { text: '18+', type: 'warning' },
    banned: { text: '⛔ Запрещено', type: 'error' },
  }
  return map[m] || null
}

function displayVerdict(row) {
  return verdictFromMarking(row.content_marking) || aiVerdict(row)
}

async function setMarking(row, v) {
  patchStart(row.id)
  try {
    await patchReport(row.id, { content_marking: v == null ? '' : v })
  } catch (e) {
    message.error(e.message || 'Не удалось сохранить маркировку')
  } finally {
    patchEnd(row.id)
  }
}

async function setRevision(row) {
  patchStart(row.id)
  try {
    await patchReport(row.id, { revision_done: true })
    message.success('Ревизия отмечена')
  } catch (e) {
    message.error(e.message || 'Ошибка')
  } finally {
    patchEnd(row.id)
  }
}

async function setEscalate(row) {
  patchStart(row.id)
  try {
    await patchReport(row.id, { escalated: true })
    message.success('Передано юристу')
  } catch (e) {
    message.error(e.message || 'Ошибка')
  } finally {
    patchEnd(row.id)
  }
}

const columns = computed(() => [
  { title: 'Файл', key: 'filename', ellipsis: { tooltip: true } },
  { title: 'Источник', key: 'source', width: 130, render: (row) => row.source || '—' },
  { title: 'Начало', key: 'started_at', width: 160, render: (row) => formatDate(row.started_at) },
  { title: 'Завершение', key: 'finished_at', width: 160, render: (row) => formatDate(row.finished_at) },
  {
    title: 'Заключение',
    key: 'ai_verdict',
    width: 138,
    render: (row) => {
      const v = displayVerdict(row)
      const hint = row.content_marking
        ? 'Заключение по сохранённой маркировке отчёта'
        : row.status === 'success'
          ? 'Предварительная оценка по числу детекций — задайте маркировку для точного статуса'
          : ''
      return h(
        NTooltip,
        { placement: 'top', disabled: !hint },
        {
          trigger: () => h(NTag, { type: v.type, size: 'small', round: true }, () => v.text),
          default: () => hint,
        },
      )
    },
  },
  { title: 'Детекций', key: 'match_count', width: 90, render: (row) => String(row.match_count ?? 0) },
  {
    title: 'Маркировка',
    key: 'content_marking',
    width: 158,
    render: (row) =>
      h(NSelect, {
        value: row.content_marking ?? null,
        options: MARKING_OPTIONS,
        size: 'small',
        disabled: !canEditMarking(row),
        style: { width: '146px' },
        placeholder: 'Выберите',
        onUpdateValue: (v) => setMarking(row, v),
      }),
  },
  {
    title: 'Портал',
    key: 'portal_actions',
    width: 108,
    render: (row) =>
      h(NSpace, { size: 4, wrap: false }, () => [
        h(
          NTooltip,
          { placement: 'top' },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  quaternary: true,
                  circle: true,
                  disabled: row.revision_done || isPatching(row.id),
                  loading: isPatching(row.id),
                  type: row.revision_done ? 'success' : 'default',
                  'aria-label': 'Ревизия выполнена',
                  onClick: () => setRevision(row),
                },
                { icon: () => h(NIcon, { component: CheckmarkDoneOutline }) },
              ),
            default: () => (row.revision_done ? 'Ревизия уже отмечена' : 'Отметить ревизию'),
          },
        ),
        h(
          NTooltip,
          { placement: 'top' },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  quaternary: true,
                  circle: true,
                  disabled: row.escalated || isPatching(row.id),
                  loading: isPatching(row.id),
                  type: row.escalated ? 'warning' : 'default',
                  'aria-label': 'Эскалация юристу',
                  onClick: () => setEscalate(row),
                },
                { icon: () => h(NIcon, { component: ScaleOutline }) },
              ),
            default: () => (row.escalated ? 'Уже у юриста' : 'Передать юристу'),
          },
        ),
      ]),
  },
  {
    title: 'Статус', key: 'status', width: 120,
    render: (row) => h(NTag, { type: statusType(row.status), size: 'small', round: true }, () => statusLabel(row.status)),
  },
  {
    title: 'Действия', key: 'actions', width: 88,
    render: (row) => h(NSpace, { size: 4 }, () => [
      h(
        NTooltip,
        { placement: 'top' },
        {
          trigger: () =>
            h(NButton, { quaternary: true, circle: true, size: 'small', onClick: () => openPlayer(row) },
              { icon: () => h(NIcon, { component: PlayOutline }) }),
          default: () => 'Плеер, PDF и детекции',
        },
      ),
      h(NPopconfirm, { onPositiveClick: () => handleDelete(row.id) },
        {
          trigger: () => h(NButton, { quaternary: true, circle: true, size: 'small', type: 'error' },
            { icon: () => h(NIcon, { component: TrashOutline }) }),
          default: () => 'Удалить отчёт?',
        }),
    ]),
  },
])

onMounted(async () => {
  await fetchReports()
  await consumeReportIdFromQuery()
})

watch(
  () => route.query.reportId,
  async (rid) => {
    if (rid == null || rid === '') return
    await fetchReports()
    await consumeReportIdFromQuery()
  },
)
</script>

<template>
  <div class="results-page">
    <div class="page-toolbar">
      <h1 class="page-title">Результаты анализа</h1>
      <div class="toolbar-actions">
        <NButton quaternary :loading="loading" :disabled="loading" @click="fetchReports">
          Обновить
        </NButton>
      </div>
    </div>

   

    <NSpin :show="loading">
      <NDataTable
        v-if="reports.length || loading"
        :columns="columns"
        :data="reports"
        :row-key="(r) => r.id"
        :bordered="true"
        :single-line="false"
        :scroll-x="1280"
        :virtual-scroll="useVirtualTable"
        :max-height="useVirtualTable ? tableMaxHeight : undefined"
        striped
      />
      <NCard v-else class="results-empty-card" :bordered="true">
        <NEmpty description="Пока нет отчётов">
          <template #extra>
            <NSpace vertical align="center" :size="12" class="results-empty-extra">
              <p class="results-empty-hint">
                Отчёты появляются после загрузки видео и завершения анализа.
              </p>
              <NSpace justify="center" :wrap="true" :size="8">
                <NButton type="primary" @click="router.push('/files')">Загруженные файлы</NButton>
                <NButton v-if="showQueueCta" @click="router.push('/operator/queue')">Очередь анализа</NButton>
              </NSpace>
            </NSpace>
          </template>
        </NEmpty>
      </NCard>
    </NSpin>

    <Transition name="linza-modal">
      <VideoPlayer
        v-if="showPlayer && playerFilename"
        :filename="playerFilename"
        :detections="playerDetections"
        :title="playerTitle"
        :report-label="playerReportLabel"
        :violations-count="playerViolationsCount"
        :vaf-job-id="playerVafJobId"
        @close="showPlayer = false"
      />
    </Transition>
  </div>
</template>

<style scoped>
.results-page { max-width: 1100px; width: 100%; margin: 0 auto; }
.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.page-title { font-size: 19px; font-weight: 600; letter-spacing: -0.02em; }
.table-hint {
  margin-bottom: 14px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.45;
  color: var(--c-txt-2);
}

.results-empty-card {
  border-radius: var(--r-lg, 12px);
}

.results-empty-card :deep(.n-card__content) {
  padding: 40px 24px 48px;
}

.results-empty-extra {
  max-width: 420px;
  margin-top: 4px;
}

.results-empty-hint {
  margin: 0;
  text-align: center;
  font-size: 13px;
  line-height: 1.5;
  color: var(--c-txt-2);
}
</style>
