<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { NSpin, NEmpty, NTag, NButton, NIcon, NAlert, NSkeleton } from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'
import { PORTAL_PERIODS, portalPeriodSubtitle } from '../utils/portalPeriod.js'

const { getToken } = useAuth()
const loading = ref(false)
const period = ref('month')
const payload = ref(null)
const err = ref('')

const AVATAR_BG = [
  'var(--c-blue)',
  'var(--c-ok)',
  'var(--c-teal)',
  'var(--c-warn)',
  'var(--c-err)',
  'var(--c-txt-2)',
]

const ROLE_LABELS = {
  administrator: 'Администратор',
  operator: 'Оператор',
  lawyer: 'Юрист',
  chief_editor: 'Главный редактор',
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const res = await fetch(`/api/portal/metrics/team?period=${period.value}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      payload.value = null
      err.value = res.status === 403 ? 'Нужна роль «Главный редактор»' : 'Не удалось загрузить команду'
      return
    }
    payload.value = await res.json()
  } catch {
    payload.value = null
    err.value = 'Ошибка сети'
  } finally {
    loading.value = false
  }
}

watch(period, load)

const periodLabel = computed(
  () => PORTAL_PERIODS.find((p) => p.key === period.value)?.label || period.value,
)

const periodHint = computed(() =>
  payload.value ? portalPeriodSubtitle(payload.value.period) : portalPeriodSubtitle(period.value),
)

const teamRows = computed(() => payload.value?.members || [])

const totals = computed(() => {
  let tf = 0
  let tv = 0
  let te = 0
  for (const t of teamRows.value) {
    tf += t.reports || 0
    tv += t.verified || 0
    te += t.escalated || 0
  }
  const pct = tf > 0 ? Math.round((tv / tf) * 100) : 0
  return { tf, tv, te, pct }
})

function fullName(m) {
  return [m.first_name, m.last_name].filter(Boolean).join(' ') || m.login || `id ${m.id}`
}

function colorAt(i) {
  return AVATAR_BG[i % AVATAR_BG.length]
}

function initials(name) {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

onMounted(load)
</script>

<template>
  <div class="editor-team">
    <div class="hdr">
      <div>
        <h1 class="page-title">Команда</h1>
        <p class="hint">
          Сводка по сотрудникам за период: созданные отчёты, завершённые ревизии и передачи на оценку юристу.
        </p>
        <p v-if="payload || (!loading && !err)" class="pg-sub">{{ periodHint }}</p>
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

    <NAlert v-if="payload" type="info" :bordered="false" class="hint-alert" closable>
      Пользователи без отчётов за период показываются с нулями — это нормально для обзора состава.
    </NAlert>

    <NSpin :show="loading">
      <div v-if="loading && !payload" class="sk">
        <NSkeleton text :repeat="2" />
        <div class="sk-cards">
          <NSkeleton height="72px" :sharp="false" class="sk-c" />
          <NSkeleton height="72px" :sharp="false" class="sk-c" />
          <NSkeleton height="72px" :sharp="false" class="sk-c" />
          <NSkeleton height="72px" :sharp="false" class="sk-c" />
        </div>
      </div>
      <NEmpty v-else-if="!payload && err" :description="err" />
      <template v-else-if="payload">
        <div class="g">
          <div class="c">
            <div class="c-t">Отчётов</div>
            <div class="c-v">{{ totals.tf }}</div>
            <div class="c-s">за {{ periodLabel.toLowerCase() }}</div>
          </div>
          <div class="c">
            <div class="c-t">Ревизий</div>
            <div class="c-v c-v-ok">{{ totals.tv }}</div>
            <div class="c-s">завершено (revision_done)</div>
          </div>
          <div class="c">
            <div class="c-t">Эскалаций</div>
            <div class="c-v c-v-warn">{{ totals.te }}</div>
            <div class="c-s">передано юристу</div>
          </div>
          <div class="c">
            <div class="c-t">Доля ревизий</div>
            <div class="c-v c-v-bl">{{ totals.pct }}%</div>
            <div class="c-s">ревизий к отчётам</div>
          </div>
        </div>

        <div class="sec-wrap">
          <h2 class="sec">Сотрудники</h2>
          <p class="sec-d">Роли портала и метрики по выбранному окну.</p>
        </div>

        <div v-if="!teamRows.length" class="empty-block">
          <NEmpty description="В системе пока нет пользователей" />
        </div>

        <div
          v-for="(t, idx) in teamRows"
          v-else
          :key="t.id"
          class="member-card"
        >
          <div class="row-top">
            <div class="av" :style="{ background: colorAt(idx) }">{{ initials(fullName(t)) }}</div>
            <div class="info">
              <div class="nm">{{ fullName(t) }}</div>
              <div class="login">{{ t.login }}</div>
              <div class="tag-row">
                <NTag
                  v-for="r in t.portal_roles || []"
                  :key="r"
                  size="small"
                  type="info"
                  :bordered="false"
                  class="role-tag"
                >
                  {{ ROLE_LABELS[r] || r }}
                </NTag>
                <span v-if="!(t.portal_roles && t.portal_roles.length)" class="no-roles">Роли портала не назначены</span>
              </div>
            </div>
            <div v-if="(t.reports || 0) > 0" class="pp">{{ t.productivity_pct }}%</div>
          </div>
          <div class="metrics">
            <div class="mi"><div class="mv">{{ t.reports }}</div><div class="ml">Отчётов</div></div>
            <div class="mi"><div class="mv mv-ok">{{ t.verified }}</div><div class="ml">Ревизий</div></div>
            <div class="mi"><div class="mv mv-warn">{{ t.escalated }}</div><div class="ml">Эскалир.</div></div>
            <div class="mi"><div class="mv" :class="{ 'mv-err': (t.pending || 0) > 0 }">{{ t.pending }}</div><div class="ml">В очереди</div></div>
          </div>
          <div v-if="(t.reports || 0) > 0" class="bar">
            <div class="bar-f" :style="{ width: `${Math.min(100, t.productivity_pct)}%` }" />
          </div>
        </div>
      </template>
    </NSpin>
  </div>
</template>

<style scoped>
.editor-team { max-width: 820px; width: 100%; margin: 0 auto; }

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 6px;
  color: var(--c-txt);
}
.hint {
  color: var(--c-txt-2);
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
  max-width: 52ch;
}
.pg-sub { font-size: 12px; color: var(--c-txt-3); margin: 10px 0 0; }
.hdr-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.seg {
  display: flex; flex-wrap: wrap; gap: 4px; padding: 4px;
  background: var(--c-surface-2); border: 1px solid var(--c-border); border-radius: 10px;
}

.hint-alert { margin-bottom: 18px; border-radius: 10px; font-size: 13px; }

.sk { margin-bottom: 20px; }
.sk-cards { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.sk-c { flex: 1; min-width: 140px; }

.g { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 8px; }
.c {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 16px 18px;
  flex: 1;
  min-width: 148px;
}
.c-t { font-size: 10px; font-weight: 600; color: var(--c-txt-2); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; }
.c-v { font-size: 26px; font-weight: 700; line-height: 1; font-variant-numeric: tabular-nums; }
.c-v-ok { color: var(--c-ok); }
.c-v-warn { color: var(--c-warn); }
.c-v-bl { color: var(--c-blue); }
.c-s { font-size: 11px; color: var(--c-txt-3); margin-top: 6px; line-height: 1.35; }

.sec-wrap { margin: 22px 0 14px; }
.sec { font-size: 15px; font-weight: 700; margin: 0 0 4px; color: var(--c-txt); letter-spacing: -0.02em; }
.sec-d { font-size: 13px; color: var(--c-txt-3); margin: 0; }

.empty-block { padding: 28px 0; }

.member-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}
.member-card:hover { border-color: var(--c-border); }

.row-top { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 14px; }
.av {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.info { flex: 1; min-width: 0; }
.nm { font-size: 14px; font-weight: 600; color: var(--c-txt); }
.login { font-size: 12px; color: var(--c-txt-3); margin: 2px 0 8px; }
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
.role-tag { margin: 0 !important; }
.no-roles { font-size: 12px; color: var(--c-txt-3); font-style: italic; }
.pp { font-size: 12px; color: var(--c-ok); font-weight: 700; flex-shrink: 0; }

.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 4px;
}
.mi { text-align: center; }
.mv { font-size: 17px; font-weight: 700; font-variant-numeric: tabular-nums; }
.mv-ok { color: var(--c-ok); }
.mv-warn { color: var(--c-warn); }
.mv-err { color: var(--c-err); }
.ml { font-size: 9px; color: var(--c-txt-3); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }

.bar { height: 5px; border-radius: 3px; background: var(--c-surface-2); overflow: hidden; margin-top: 10px; }
.bar-f { height: 100%; border-radius: 3px; background: var(--c-ok); transition: width 0.35s ease; }
</style>
