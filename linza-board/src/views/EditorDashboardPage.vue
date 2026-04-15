<script setup>
import { ref, computed, onMounted, watch, h } from 'vue'
import { NButton, NSpin, NEmpty, NDataTable, NTag, NIcon, NAlert, NSkeleton } from 'naive-ui'
import { RefreshOutline, DocumentTextOutline, TimeOutline, CheckmarkDoneOutline, WarningOutline } from '@vicons/ionicons5'
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
      err.value = res.status === 403 ? 'Нужна роль «Главный редактор»' : 'Не удалось загрузить метрики'
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

const markingTotal = computed(() =>
  (summary.value?.marking || []).reduce((s, x) => s + (x.count || 0), 0),
)

const donutMarkingStyle = computed(() => {
  const rows = summary.value?.marking || []
  const t = markingTotal.value || 1
  let acc = 0
  const parts = []
  for (const d of rows) {
    if (!d.count) continue
    const start = (acc / t) * 360
    acc += d.count
    const end = (acc / t) * 360
    parts.push(`${d.color} ${start}deg ${end}deg`)
  }
  if (!parts.length) return { background: 'conic-gradient(var(--c-border) 0deg 360deg)' }
  return { background: `conic-gradient(${parts.join(', ')})` }
})

const procRows = computed(() => summary.value?.processing || [])

const procTotal = computed(() => procRows.value.reduce((s, x) => s + (x.count || 0), 0))

/** Доля «готово» среди сегментов диаграммы статусов обработки. */
const procReadyPct = computed(() => {
  const rows = procRows.value
  const success = rows.find((x) => x.key === 'success')?.count ?? 0
  const t = procTotal.value
  if (!t) return null
  return Math.min(100, Math.round((success / t) * 100))
})

const donutProcStyle = computed(() => {
  const rows = procRows.value
  const t = procTotal.value || 1
  let acc = 0
  const parts = []
  for (const d of rows) {
    if (!d.count) continue
    const start = (acc / t) * 360
    acc += d.count
    const end = (acc / t) * 360
    parts.push(`${d.color} ${start}deg ${end}deg`)
  }
  if (!parts.length) return { background: 'conic-gradient(var(--c-border) 0deg 360deg)' }
  return { background: `conic-gradient(${parts.join(', ')})` }
})

const critCols = [
  { title: 'Файл', key: 'filename', ellipsis: { tooltip: true } },
  {
    title: 'Детекций',
    key: 'match_count',
    width: 96,
    align: 'right',
    titleAlign: 'right',
  },
  {
    title: 'Причина',
    key: 'why',
    width: 120,
    render: (r) =>
      h(
        NTag,
        { size: 'small', type: 'error', round: true },
        () => (r.content_marking === 'banned' ? 'Запрещено' : 'Ошибка анализа'),
      ),
  },
]

onMounted(load)
</script>

<template>
  <div class="dash">
    <div class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">Дашборд</h1>
        <p class="pg-d">Сводные показатели по отчётам, очереди анализа и критическим материалам за выбранный период.</p>
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
      Данные обновляются при смене периода и отражают актуальное состояние отчётов и очереди.
    </NAlert>

    <NSpin :show="loading">
      <div v-if="loading && !summary" class="sk">
        <NSkeleton text :repeat="2" />
        <div class="sk-row">
          <NSkeleton height="88px" width="22%" :sharp="false" />
          <NSkeleton height="88px" width="22%" :sharp="false" />
          <NSkeleton height="88px" width="22%" :sharp="false" />
          <NSkeleton height="88px" width="22%" :sharp="false" />
        </div>
      </div>
      <NEmpty v-else-if="!summary && err" :description="err" />
      <template v-else-if="summary">
        <div class="g kpi-row">
          <div class="kpi accent-doc">
            <div class="kpi-ic"><NIcon :component="DocumentTextOutline" :size="20" /></div>
            <div class="kpi-body">
              <div class="c-t">Всего отчётов</div>
              <div class="c-v">{{ summary.kpi.reports_total }}</div>
              <div class="c-s">в выбранном окне</div>
            </div>
          </div>
          <div class="kpi accent-time">
            <div class="kpi-ic"><NIcon :component="TimeOutline" :size="20" /></div>
            <div class="kpi-body">
              <div class="c-t">В очереди API</div>
              <div class="c-v kpi-num-warn">{{ summary.kpi.queue_active }}</div>
              <div class="c-s">ожидают или в работе</div>
            </div>
          </div>
          <div class="kpi accent-ok">
            <div class="kpi-ic"><NIcon :component="CheckmarkDoneOutline" :size="20" /></div>
            <div class="kpi-body">
              <div class="c-t">Ревизий завершено</div>
              <div class="c-v kpi-num-ok">{{ summary.kpi.revisions_done }}</div>
              <div class="c-s">по флагу в отчёте</div>
            </div>
          </div>
          <div class="kpi accent-warn">
            <div class="kpi-ic"><NIcon :component="WarningOutline" :size="20" /></div>
            <div class="kpi-body">
              <div class="c-t">Критические</div>
              <div class="c-v kpi-num-err">{{ summary.kpi.critical }}</div>
              <div class="c-s">запрет или сбой</div>
            </div>
          </div>
        </div>

        <div class="g charts">
          <div class="c wide chart-card">
            <div class="c-t">Маркировка контента</div>
            <p class="c-hint">Только успешные отчёты с известным распределением по возрасту.</p>
            <div class="dw">
              <div class="dn" :title="`${markingTotal} отчётов`">
                <div class="donut" :style="donutMarkingStyle" />
                <div class="dn-c">
                  <div class="dn-v">{{ markingTotal }}</div>
                  <div class="dn-l">успешных</div>
                </div>
              </div>
              <div class="lg">
                <div v-for="d in summary.marking" :key="d.key" class="lg-i">
                  <div class="lg-d" :style="{ background: d.color }" />
                  <span class="lg-lbl">{{ d.label }}</span>
                  <span class="lg-v">{{ d.count }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="c wide chart-card">
            <div class="c-t">Статус обработки</div>
            <p class="c-hint">Сводка по отчётам за период и по текущей очереди обработки.</p>
            <div class="dw">
              <div class="dn sm" :title="procReadyPct != null ? `${procReadyPct}% готово` : ''">
                <div class="donut sm" :style="donutProcStyle" />
                <div class="dn-c">
                  <div class="dn-v">{{ procReadyPct != null ? `${procReadyPct}%` : '—' }}</div>
                  <div class="dn-l">доля «успех» в круге</div>
                </div>
              </div>
              <div class="lg">
                <div v-for="d in summary.processing" :key="d.key" class="lg-i">
                  <div class="lg-d" :style="{ background: d.color }" />
                  <span class="lg-lbl">{{ d.label }}</span>
                  <span class="lg-v">{{ d.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="sec-wrap">
          <h2 class="sec">Критические файлы</h2>
          <p class="sec-d">Требуют внимания: маркировка «Запрещено» или статус ошибки.</p>
        </div>
        <NDataTable
          v-if="summary.critical_files?.length"
          :columns="critCols"
          :data="summary.critical_files"
          :bordered="false"
          size="small"
          :single-line="false"
          class="crit-table"
        />
        <div v-else class="empty-crit">
          <NEmpty description="Критических записей нет — хороший знак" />
        </div>
      </template>
    </NSpin>
  </div>
</template>

<style scoped>
.dash { max-width: 1040px; width: 100%; margin: 0 auto; }

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}
.hdr-txt { min-width: 0; flex: 1; }
.pg-t {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 6px;
  color: var(--c-txt);
}
.pg-d {
  font-size: 14px;
  line-height: 1.5;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 52ch;
}
.pg-sub {
  font-size: 12px;
  color: var(--c-txt-3);
  margin: 10px 0 0;
}
.hdr-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.seg {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 4px;
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  border-radius: 10px;
}

.hint-alert {
  margin-bottom: 20px;
  border-radius: 10px;
  font-size: 13px;
}

.sk { margin-bottom: 24px; }
.sk-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.g {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}
.charts { align-items: stretch; }

.kpi-row { margin-bottom: 8px; }

.kpi {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 16px 18px;
  flex: 1;
  min-width: 200px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.kpi:hover {
  border-color: var(--c-border);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.kpi-ic {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--c-blue);
  background: var(--c-blue-dim);
}
.accent-time .kpi-ic {
  color: var(--c-blue);
  background: var(--c-blue-dim);
}
.accent-ok .kpi-ic {
  color: var(--c-ok);
  background: var(--c-ok-bg);
}
.accent-warn .kpi-ic {
  color: var(--c-err);
  background: var(--c-err-bg);
}
.accent-doc .kpi-ic {
  color: var(--c-txt-2);
  background: var(--c-surface-2);
}
.kpi-body { min-width: 0; }
.c-t {
  font-size: 10px;
  font-weight: 600;
  color: var(--c-txt-2);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 8px;
}
.c-v {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}
.kpi-num-ok { color: var(--c-ok); }
.kpi-num-warn { color: var(--c-blue); }
.kpi-num-err { color: var(--c-err); }
.c-s {
  font-size: 11px;
  color: var(--c-txt-3);
  margin-top: 6px;
  line-height: 1.35;
}

.c {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 18px 20px;
  flex: 1;
  min-width: 260px;
}
.c.wide { min-width: 280px; }
.chart-card { min-height: 200px; }
.c-hint {
  font-size: 12px;
  color: var(--c-txt-3);
  margin: -4px 0 14px;
  line-height: 1.45;
}
.c-t {
  margin-bottom: 4px;
}

.dw { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; }
.dn { position: relative; width: 108px; height: 108px; flex-shrink: 0; }
.dn.sm { width: 96px; height: 96px; }
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
.dn-v {
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.dn-l {
  font-size: 9px;
  color: var(--c-txt-3);
  text-align: center;
  padding: 0 6px;
  line-height: 1.25;
  max-width: 72px;
}
.lg {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 160px;
}
.lg-i {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.lg-d { width: 8px; height: 8px; border-radius: 3px; flex-shrink: 0; }
.lg-lbl { color: var(--c-txt-2); flex: 1; min-width: 0; }
.lg-v {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--c-txt);
}

.sec-wrap { margin: 28px 0 12px; }
.sec {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  color: var(--c-txt);
}
.sec-d {
  font-size: 13px;
  color: var(--c-txt-3);
  margin: 0;
  line-height: 1.45;
}
.crit-table :deep(.n-data-table-th) { font-size: 10px; }
.empty-crit {
  padding: 28px 16px;
  background: var(--c-surface);
  border: 1px dashed var(--c-border);
  border-radius: 14px;
}
</style>
