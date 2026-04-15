<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NDataTable,
  NTag,
  NSpin,
  NEmpty,
  NIcon,
  NTooltip,
  NSpace,
  NPopconfirm,
  useMessage,
} from 'naive-ui'
import { RefreshOutline, ListOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'

const { getToken } = useAuth()
const router = useRouter()
const message = useMessage()

const rows = ref([])
const loading = ref(false)

const QUEUE_URL = '/api/analysis-queue/'

const VIRTUAL_MIN = 28
const tableMaxHeight = 520
const useVirtual = computed(() => rows.value.length >= VIRTUAL_MIN)

let pollTimer = null

function authHeaders() {
  return { Authorization: `Bearer ${getToken()}` }
}

function clearPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function syncPolling() {
  clearPoll()
  const active = rows.value.some((r) => r.status === 'pending' || r.status === 'processing')
  if (active) {
    pollTimer = setInterval(load, 3000)
  }
}

function shortFileName(storageKey) {
  if (!storageKey) return '—'
  return storageKey.replace(/^(uploads\/|sources\/)/, '')
}

function statusLabel(s) {
  if (s === 'pending') return 'В очереди'
  if (s === 'processing') return 'В работе'
  if (s === 'done') return 'Готово'
  if (s === 'error') return 'Ошибка'
  return s || '—'
}

function statusTagType(s) {
  if (s === 'pending') return 'warning'
  if (s === 'processing') return 'info'
  if (s === 'done') return 'success'
  if (s === 'error') return 'error'
  return 'default'
}

function formatWhen(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function load() {
  loading.value = true
  try {
    const res = await fetch(QUEUE_URL, { headers: authHeaders() })
    if (res.ok) {
      rows.value = await res.json()
    } else {
      rows.value = []
      message.warning('Не удалось загрузить очередь')
    }
  } catch {
    rows.value = []
    message.error('Ошибка сети')
  } finally {
    loading.value = false
    syncPolling()
  }
}

async function removeRow(id) {
  try {
    const res = await fetch(`${QUEUE_URL}${id}`, { method: 'DELETE', headers: authHeaders() })
    if (!res.ok) throw new Error('delete')
    await load()
  } catch {
    message.error('Не удалось убрать задачу')
  }
}

function openReport(reportId) {
  if (reportId == null) return
  router.push({ path: '/results', query: { reportId: String(reportId) } })
}

const columns = computed(() => [
  {
    title: 'Файл',
    key: 'storage_key',
    ellipsis: { tooltip: true },
    render: (r) => shortFileName(r.storage_key),
  },
  {
    title: 'Источник',
    key: 'origin',
    width: 110,
    render: (r) =>
      h(
        NTag,
        { size: 'small', round: true, bordered: false, type: 'default' },
        () => (r.origin === 'source' ? 'Источник' : 'Загрузка'),
      ),
  },
  {
    title: 'Статус',
    key: 'status',
    minWidth: 240,
    render: (r) => {
      const label = statusLabel(r.status)
      const tag = h(NTag, { type: statusTagType(r.status), size: 'small', round: true }, () => label)
      const detail = (r.status_detail || '').trim()
      const vp = r.vaf_progress
      const pct =
        vp != null && typeof vp.progress === 'number' && !Number.isNaN(vp.progress)
          ? `${Math.round(vp.progress)}%`
          : ''

      /** Одна строка: кадры + % или текст этапа (аудио) + % */
      let sub = ''
      if (r.status === 'processing' && vp && vp.frames_total != null && Number(vp.frames_total) > 0) {
        const fd = Number(vp.frames_done ?? 0)
        const ft = Number(vp.frames_total)
        if (fd < ft) {
          sub = pct ? `Кадры: ${fd}/${ft} · ${pct}` : `Кадры: ${fd}/${ft}`
        } else {
          sub = [detail || '', pct].filter(Boolean).join(' · ')
        }
      } else {
        sub = [detail, pct].filter(Boolean).join(' · ')
      }

      const tip = sub || ''

      const cell = h('div', { class: 'queue-status-cell' }, [
        tag,
        sub ? h('div', { class: 'queue-status-detail' }, sub) : null,
      ])

      if (r.status === 'error' && r.error_message) {
        return h(NTooltip, { placement: 'top', style: { maxWidth: '400px' } }, {
          trigger: () => cell,
          default: () => r.error_message,
        })
      }
      if (tip && (r.status === 'processing' || r.status === 'pending')) {
        return h(NTooltip, { placement: 'top', style: { maxWidth: '400px' } }, {
          trigger: () => cell,
          default: () => tip,
        })
      }
      return cell
    },
  },
  {
    title: 'Создано',
    key: 'created_at',
    width: 148,
    render: (r) => formatWhen(r.created_at),
  },
  {
    title: '',
    key: 'actions',
    width: 200,
    render: (r) =>
      h(NSpace, { size: 8, wrap: false }, () => {
        const btns = []
        if (r.status === 'done' && r.report_id != null) {
          btns.push(
            h(
              NButton,
              {
                size: 'small',
                type: 'primary',
                secondary: true,
                onClick: () => openReport(r.report_id),
              },
              { default: () => 'К отчёту' },
            ),
          )
        }
        btns.push(
          h(
            NPopconfirm,
            {
              onPositiveClick: () => removeRow(r.id),
            },
            {
              trigger: () =>
                h(NButton, { size: 'small', quaternary: true }, { default: () => 'Убрать' }),
              default: () => 'Убрать задачу из списка?',
            },
          ),
        )
        return btns
      }),
  },
])

onMounted(load)
onUnmounted(() => {
  clearPoll()
})
</script>

<template>
  <div class="queue-page">
    <header class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">
          <NIcon :component="ListOutline" class="hdr-ic" />
          Очередь анализа
        </h1>
        <p class="pg-d">
          Здесь отображаются файлы, отправленные на обработку. Пока есть задачи в ожидании или в работе, список обновляется автоматически.
        </p>
      </div>
      <NButton quaternary :loading="loading" @click="load">
        <template #icon><NIcon :component="RefreshOutline" /></template>
        Обновить
      </NButton>
    </header>

    <NSpin :show="loading && !rows.length">
      <NDataTable
        v-if="rows.length"
        :columns="columns"
        :data="rows"
        :row-key="(r) => r.id"
        :bordered="true"
        :single-line="false"
        size="small"
        striped
        :scroll-x="1040"
        :virtual-scroll="useVirtual"
        :max-height="useVirtual ? tableMaxHeight : undefined"
        class="queue-table"
      />
      <div v-else-if="!loading" class="empty-wrap">
        <NEmpty description="Очередь пуста. Отправьте готовые файлы из раздела «Загруженные файлы»." />
      </div>
    </NSpin>
  </div>
</template>

<style scoped>
.queue-page {
  max-width: 1120px;
  width: 100%;
  margin: 0 auto;
  padding-bottom: 24px;
}

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
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
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  color: var(--c-txt-2);
  max-width: 56ch;
}

.empty-wrap {
  padding: 48px 20px;
  background: var(--c-surface);
  border: 1px dashed var(--c-border);
  border-radius: var(--r-lg);
}

.queue-table :deep(.n-data-table-th) {
  font-size: 11px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.queue-table :deep(.queue-status-cell) {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  padding: 4px 0;
  max-width: 320px;
}

.queue-table :deep(.queue-status-detail) {
  font-size: 12px;
  line-height: 1.35;
  color: var(--c-txt-2);
  font-weight: 450;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
