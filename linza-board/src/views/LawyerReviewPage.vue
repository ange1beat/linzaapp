<script setup>
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton,
  NDataTable,
  NSpin,
  NAlert,
  NIcon,
  NSpace,
  NSelect,
  NPopconfirm,
  useMessage,
} from 'naive-ui'
import { RefreshOutline, PlayOutline, CheckmarkCircleOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'
import { useReports } from '../composables/useReports.js'
import VideoPlayer from '../components/VideoPlayer.vue'
import { extractAndNormalize } from '../composables/detectionsPayload.js'
import { extractVafJobId } from '../utils/vafJobId.js'

const { getToken } = useAuth()
const { getReport, patchReport } = useReports()
const message = useMessage()
const rows = ref([])
const loading = ref(false)
const loadError = ref('')
const showPlayer = ref(false)
const playerFilename = ref('')
const playerDetections = ref([])
const playerTitle = ref('')
const playerVafJobId = ref('')
const patching = ref(new Set())

const MARKING_OPTIONS = [
  { label: 'Не задана', value: null },
  { label: 'Чисто (0+)', value: 'clean' },
  { label: '12+', value: 'age_12' },
  { label: '16+', value: 'age_16' },
  { label: '18+', value: 'age_18' },
  { label: 'Запрещено', value: 'banned' },
]

function isPatching(id) {
  return patching.value.has(id)
}

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

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await fetch('/api/portal/lawyer/escalated-reports', {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      rows.value = []
      loadError.value = res.status === 403 ? 'Нужна роль «Юрист» портала' : 'Не удалось загрузить список'
      return
    }
    rows.value = await res.json()
  } catch {
    rows.value = []
    loadError.value = 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

const showEmptyOk = computed(
  () => !loading.value && !loadError.value && rows.value.length === 0,
)

async function openPlayer(report) {
  playerTitle.value = report.filename
  let list = []
  playerVafJobId.value = ''
  try {
    const full = await getReport(report.id)
    const raw = full.report_json
    if (raw != null && String(raw).trim() !== '') {
      const j = typeof raw === 'string' ? JSON.parse(raw) : raw
      list = extractAndNormalize(j).list
      playerVafJobId.value = extractVafJobId(j)
    }
  } catch {
    list = []
  }
  playerFilename.value = report.filename
  playerDetections.value = list
  showPlayer.value = true
}

async function setLawyerMarking(row, v) {
  patchStart(row.id)
  try {
    await patchReport(row.id, { content_marking: v == null ? '' : v })
    row.content_marking = v
    message.success('Маркировка сохранена')
  } catch (e) {
    message.error(e.message || 'Не удалось сохранить')
  } finally {
    patchEnd(row.id)
  }
}

async function completeLawyerReview(row) {
  patchStart(row.id)
  try {
    await patchReport(row.id, { escalated: false })
    message.success('Рассмотрение завершено, отчёт убран из списка юриста')
    rows.value = rows.value.filter((r) => r.id !== row.id)
  } catch (e) {
    message.error(e.message || 'Не удалось завершить')
  } finally {
    patchEnd(row.id)
  }
}

const columns = computed(() => [
  { title: 'Файл', key: 'filename', ellipsis: { tooltip: true } },
  {
    title: 'Маркировка',
    key: 'cm',
    width: 168,
    render: (row) =>
      h(NSelect, {
        value: row.content_marking ?? null,
        options: MARKING_OPTIONS,
        size: 'small',
        disabled: isPatching(row.id),
        style: { width: '156px' },
        placeholder: 'Выберите',
        onUpdateValue: (v) => setLawyerMarking(row, v),
      }),
  },
  { title: 'Совпадения', key: 'match_count', width: 110, align: 'right', titleAlign: 'right' },
  {
    title: 'Действия',
    key: 'actions',
    width: 200,
    render: (row) =>
      h(NSpace, { size: 8, wrap: false }, () => [
        h(
          NButton,
          {
            size: 'small',
            quaternary: true,
            circle: true,
            disabled: isPatching(row.id),
            'aria-label': `Просмотр: ${row.filename}`,
            onClick: () => openPlayer(row),
          },
          { icon: () => h(NIcon, { component: PlayOutline }) },
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => completeLawyerReview(row),
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'primary',
                  secondary: true,
                  disabled: isPatching(row.id),
                  loading: isPatching(row.id),
                },
                () => 'Завершить рассмотрение',
              ),
            default: () =>
              'Снять эскалацию: отчёт исчезнет из этого списка. Маркировку при необходимости задайте выше.',
          },
        ),
      ]),
  },
])

onMounted(load)
</script>

<template>
  <div class="lawyer-page">
    <div class="hdr">
      <div>
        <h1 class="page-title">На рассмотрении</h1>
        <p class="hint">
          Отчёты, переданные оператором или главным редактором (кнопка «Юристу» в «Результаты»). Уточните маркировку при
          необходимости и нажмите «Завершить рассмотрение», чтобы снять эскалацию. Пока отчёт здесь или уже отмечена ревизия
          оператором, маркировку меняют только юрист, главный редактор или администратор портала (проверка на сервере).
        </p>
      </div>
      <NButton quaternary circle :loading="loading" aria-label="Обновить" @click="load">
        <template #icon><NIcon :component="RefreshOutline" /></template>
      </NButton>
    </div>

    <NSpin :show="loading">
      <NAlert v-if="loadError" type="error" :bordered="false" class="err-alert">
        {{ loadError }}
      </NAlert>
      <template v-else-if="rows.length">
        <NDataTable
          :columns="columns"
          :data="rows"
          :bordered="false"
          :single-line="false"
          :scroll-x="920"
          size="small"
          class="law-table"
        />
      </template>
      <div v-else-if="showEmptyOk" class="state-box state-ok">
        <div class="ok-ic" aria-hidden="true">
          <NIcon :component="CheckmarkCircleOutline" :size="48" />
        </div>
        <div class="ok-title">Нет эскалированных отчётов</div>
        <p class="ok-desc">Когда главный редактор или оператор нажмёт «Юристу» в результатах, файл появится здесь.</p>
      </div>
    </NSpin>

    <Transition name="linza-modal">
      <VideoPlayer
        v-if="showPlayer && playerFilename"
        :filename="playerFilename"
        :detections="playerDetections"
        :title="playerTitle"
        :vaf-job-id="playerVafJobId"
        @close="showPlayer = false"
      />
    </Transition>
  </div>
</template>

<style scoped>
.lawyer-page { max-width: 1100px; width: 100%; margin: 0 auto; }

.hdr {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 8px;
  color: var(--c-txt);
}
.hint {
  color: var(--c-txt-2);
  font-size: 14px;
  line-height: 1.55;
  margin: 0;
  max-width: 62ch;
}
.hint code { font-size: 12px; }

.err-alert { margin-bottom: 16px; border-radius: 12px; }
.state-ok {
  text-align: center;
  padding: 48px 24px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
}
.ok-ic {
  color: var(--c-ok);
  opacity: 0.85;
  margin-bottom: 16px;
}
.ok-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--c-txt);
  margin-bottom: 8px;
}
.ok-desc {
  font-size: 14px;
  color: var(--c-txt-2);
  line-height: 1.5;
  margin: 0 auto;
  max-width: 400px;
}

.law-table :deep(.n-data-table-th) {
  font-size: 10px;
  letter-spacing: 0.04em;
}
</style>
