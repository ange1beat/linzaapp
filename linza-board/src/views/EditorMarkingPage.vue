<script setup>
/**
 * Маркировка главного редактора — метрики портала (summary API).
 */
import { ref, computed, onMounted, watch, h } from 'vue'
import { NTag, NButton, NSpin, NEmpty, NDataTable, NIcon, NAlert, NSkeleton } from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'
import { PORTAL_PERIODS, portalPeriodSubtitle } from '../utils/portalPeriod.js'

const { getToken } = useAuth()
const period = ref('month')
const loading = ref(false)
const summary = ref(null)
const err = ref('')

async function load() {
  loading.value = true
  err.value = ''
  try {
    const res = await fetch(`/api/portal/metrics/summary?period=${period.value}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      summary.value = null
      err.value = res.status === 403 ? 'Нужна роль «Главный редактор»' : 'Не удалось загрузить данные'
      return
    }
    summary.value = await res.json()
  } catch {
    summary.value = null
    err.value = 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

watch(period, load)

const periodHint = computed(() =>
  summary.value
    ? portalPeriodSubtitle(summary.value.period, summary.value.period_days)
    : portalPeriodSubtitle(period.value),
)

const markingRows = computed(() => summary.value?.marking || [])

const total = computed(() => markingRows.value.reduce((s, x) => s + (x.count || 0), 0))

const maxV = computed(() => Math.max(...markingRows.value.map((x) => x.count || 0), 1))

const donutStyle = computed(() => {
  const t = total.value || 1
  let acc = 0
  const parts = []
  for (const d of markingRows.value) {
    if (!d.count) continue
    const start = (acc / t) * 360
    acc += d.count
    const end = (acc / t) * 360
    parts.push(`${d.color} ${start}deg ${end}deg`)
  }
  if (!parts.length) return { background: 'conic-gradient(var(--c-border) 0deg 360deg)' }
  return { background: `conic-gradient(${parts.join(', ')})` }
})

function pct(count) {
  const t = total.value
  if (!t) return 0
  return Math.round((count / t) * 100)
}

function markTagType(key) {
  if (key === 'banned') return 'error'
  if (key === 'unclassified') return 'default'
  return 'info'
}

const editorial = computed(() => summary.value?.editorial_queue || [])

const editorialCols = computed(() => {
  const rows = markingRows.value
  return [
    { title: 'Файл', key: 'filename', ellipsis: { tooltip: true } },
    {
      title: 'Маркировка',
      key: 'mark',
      width: 140,
      render: (r) => {
        const k = r.content_marking || 'unclassified'
        const label = rows.find((x) => x.key === k)?.label || '—'
        return h(NTag, { size: 'small', type: markTagType(k), round: true }, () => label)
      },
    },
    {
      title: 'Задание',
      key: 'task',
      ellipsis: { tooltip: true },
      render: (r) => r.task || '—',
    },
    {
      title: 'Статус',
      key: 'st',
      width: 120,
      render: () => h(NTag, { size: 'small', type: 'default', round: true }, () => 'Ожидает ревизии'),
    },
  ]
})

onMounted(load)
</script>

<template>
  <div class="mark-page">
    <div class="hdr">
      <div>
        <h1 class="pg-t">Маркировка</h1>
        <p class="pg-d">Распределение по возрастным меткам и материалы, требующие ручной доработки.</p>
        <p v-if="summary || (!loading && !err)" class="pg-sub">{{ periodHint }}</p>
      </div>
      <div class="hdr-actions">
        <div class="seg" role="tablist" aria-label="Период">
          <NButton
            v-for="p in PORTAL_PERIODS"
            :key="p.key"
            size="small"
            :quaternary="period !== p.key"
            :type="period === p.key ? 'primary' : 'default'"
            @click="period = p.key"
          >
            {{ p.label }}
          </NButton>
        </div>
        <NButton quaternary circle :loading="loading" aria-label="Обновить" @click="load">
          <template #icon><NIcon :component="RefreshOutline" /></template>
        </NButton>
      </div>
    </div>

    <NAlert v-if="summary" type="info" :bordered="false" class="hint-alert" closable>
      В блоке «На редактуре» показаны успешные отчёты с детекциями, где ещё не стоят «Ревизия» и «Эскалация».
    </NAlert>

    <NSpin :show="loading">
      <div v-if="loading && !summary" class="sk">
        <NSkeleton text :repeat="2" />
        <div class="sk-charts">
          <NSkeleton height="180px" :sharp="false" class="sk-b" />
          <NSkeleton height="180px" :sharp="false" class="sk-b" />
        </div>
      </div>
      <NEmpty v-else-if="!summary && err" :description="err" />
      <template v-else-if="summary">
        <div class="g">
          <div class="c wide">
            <div class="c-t">Диаграмма</div>
            <div class="dw">
              <div class="dn" :title="`${total} успешных отчётов`">
                <div class="donut" :style="donutStyle" />
                <div class="dn-c">
                  <div class="dn-v">{{ total }}</div>
                  <div class="dn-l">успешных</div>
                </div>
              </div>
              <div class="lg">
                <div v-for="d in markingRows" :key="d.key" class="lg-i">
                  <div class="lg-d" :style="{ background: d.color }" />
                  <span class="lg-n">{{ d.label }}</span>
                  <span class="lg-v">
                    {{ d.count }}
                    <span v-if="total" class="pct">({{ pct(d.count) }}%)</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="c hist">
            <div class="c-t">Гистограмма</div>
            <div v-for="d in markingRows" :key="'h-' + d.key" class="hist-row">
              <div class="hist-h">
                <span>{{ d.label }}</span>
                <span class="hist-n">{{ d.count }}</span>
              </div>
              <div class="bar">
                <div
                  class="bar-f"
                  :style="{ width: `${((d.count || 0) / maxV) * 100}%`, background: d.color }"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="sec-wrap">
          <h2 class="sec">На редактуре</h2>
          <p class="sec-d">Файлы, по которым оператор ещё не закрыл ревизию и не передал спор на юриста.</p>
        </div>
        <NDataTable
          v-if="editorial.length"
          :columns="editorialCols"
          :data="editorial"
          :bordered="false"
          size="small"
          :row-key="(r) => r.id"
          :scroll-x="620"
          class="ed-table"
        />
        <div v-else class="empty-ed">
          <NEmpty description="Очередь пуста — нечего дорабатывать по этим правилам" />
        </div>
      </template>
    </NSpin>
  </div>
</template>

<style scoped>
.mark-page { max-width: 980px; width: 100%; margin: 0 auto; }

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
}
.pg-t {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 6px;
  color: var(--c-txt);
}
.pg-d {
  font-size: 14px;
  line-height: 1.5;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 48ch;
}
.pg-sub { font-size: 12px; color: var(--c-txt-3); margin: 10px 0 0; }
.hdr-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.seg {
  display: flex; flex-wrap: wrap; gap: 4px; padding: 4px;
  background: var(--c-surface-2); border: 1px solid var(--c-border); border-radius: 10px;
}

.hint-alert { margin-bottom: 18px; border-radius: 10px; font-size: 13px; }

.sk { margin-bottom: 20px; }
.sk-charts { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
.sk-b { flex: 1; min-width: 260px; }

.g { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.c {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 18px;
  flex: 1;
  min-width: 240px;
}
.c.wide { min-width: 300px; }
.c-t {
  font-size: 10px;
  font-weight: 600;
  color: var(--c-txt-2);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.dw { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.dn { position: relative; width: 120px; height: 120px; flex-shrink: 0; }
.donut {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  mask: radial-gradient(transparent 55%, black 56%);
  -webkit-mask: radial-gradient(transparent 55%, black 56%);
}
.dn-c {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.dn-v { font-size: 22px; font-weight: 700; line-height: 1; font-variant-numeric: tabular-nums; }
.dn-l { font-size: 9px; color: var(--c-txt-3); margin-top: 4px; text-align: center; }
.lg { display: flex; flex-direction: column; gap: 8px; flex: 1; min-width: 180px; }
.lg-i { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--c-txt); }
.lg-d { width: 8px; height: 8px; border-radius: 3px; flex-shrink: 0; }
.lg-n { flex: 1; min-width: 0; color: var(--c-txt-2); }
.lg-v { margin-left: auto; font-weight: 600; font-variant-numeric: tabular-nums; }
.pct { font-weight: 400; color: var(--c-txt-3); }

.hist-row { margin-bottom: 10px; }
.hist-h { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
.hist-n { font-weight: 600; color: var(--c-txt); font-variant-numeric: tabular-nums; }
.bar { height: 5px; border-radius: 3px; background: var(--c-surface-2); overflow: hidden; }
.bar-f { height: 100%; border-radius: 3px; }

.sec-wrap { margin: 24px 0 12px; }
.sec {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  color: var(--c-txt);
}
.sec-d { font-size: 13px; color: var(--c-txt-3); margin: 0; line-height: 1.45; }

.ed-table :deep(.n-data-table-th) { font-size: 10px; }

.empty-ed {
  padding: 32px 16px;
  background: var(--c-surface);
  border: 1px dashed var(--c-border);
  border-radius: 14px;
}
</style>
