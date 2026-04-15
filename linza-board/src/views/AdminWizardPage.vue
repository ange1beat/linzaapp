<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NSteps, NStep, NCard, NButton, NSpace, NSpin, NAlert, NSwitch } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useAuth } from '../composables/useAuth.js'
import {
  WIZARD_SEGMENTS,
  WIZARD_CONTENT_TYPES,
  WIZARD_PLATFORMS,
  SEGMENT_CONTENT_REC,
  SEGMENT_PLATFORM_REC,
  WIZARD_SOURCES,
  ROLES_BY_SEGMENT,
  COMPLIANCE_CLASSES,
  MATRIX_CELL_ICONS,
  MATRIX_CELL_COLORS,
} from '../data/adminWizardCatalog.js'

const message = useMessage()
const router = useRouter()
const { getToken } = useAuth()

const loading = ref(true)
const saving = ref(false)
const current = ref(1)
const err = ref('')

const form = ref({
  segment: 'tv',
  content_types: [...(SEGMENT_CONTENT_REC.tv || [])],
  platforms: [...(SEGMENT_PLATFORM_REC.tv || [])],
  sources_enabled: ['local'],
})

const ALLOWED_SOURCE_IDS = new Set(WIZARD_SOURCES.map((s) => s.id))

function normalizeLoadedSources(arr) {
  if (!Array.isArray(arr)) return ['local']
  const mapped = arr.map((id) => (id === 'yandex' ? 'yadisk' : id))
  const filtered = mapped.filter((id) => ALLOWED_SOURCE_IDS.has(id))
  return filtered.length ? filtered : ['local']
}

const activeTypes = computed(() =>
  WIZARD_CONTENT_TYPES.filter((t) => form.value.content_types.includes(t.id)),
)

const recommendedCt = computed(() => SEGMENT_CONTENT_REC[form.value.segment] || [])
const recommendedPl = computed(() => SEGMENT_PLATFORM_REC[form.value.segment] || [])

const segmentRoles = computed(() => ROLES_BY_SEGMENT[form.value.segment] || ROLES_BY_SEGMENT.tv)

/** Как setSeg() в HTML: при смене сегмента подставляются рекомендованные типы и платформы. */
function selectSegment(id) {
  form.value.segment = id
  form.value.content_types = [...(SEGMENT_CONTENT_REC[id] || ['film', 'news'])]
  form.value.platforms = [...(SEGMENT_PLATFORM_REC[id] || ['fed_tv'])]
}

function toggleSource(id, on) {
  const s = new Set(form.value.sources_enabled)
  if (on) s.add(id)
  else s.delete(id)
  form.value.sources_enabled = [...s]
}

function cellVal(sub, typeId) {
  return sub.m[typeId] || 'na'
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const res = await fetch('/api/portal/org-config', {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (res.ok) {
      const j = await res.json()
      const d = j.data || {}
      if (Object.keys(d).length) {
        const src = d.sources_enabled ?? d.sourcesEnabled
        form.value = {
          segment: d.segment ?? 'tv',
          content_types: d.content_types?.length ? d.content_types : form.value.content_types,
          platforms: d.platforms?.length ? d.platforms : form.value.platforms,
          sources_enabled: src?.length ? normalizeLoadedSources(src) : ['local'],
        }
      }
    }
  } catch {
    err.value = 'Не удалось загрузить конфигурацию'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  err.value = ''
  try {
    const res = await fetch('/api/portal/org-config', {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: form.value }),
    })
    if (!res.ok) {
      err.value = 'Ошибка сохранения'
      return
    }
    message.success('Конфигурация сохранена')
  } catch {
    err.value = 'Ошибка соединения'
  } finally {
    saving.value = false
  }
}

function goUsers() {
  router.push('/users')
}

const overviewSeg = computed(() => WIZARD_SEGMENTS.find((s) => s.id === form.value.segment))

onMounted(load)
</script>

<template>
  <div class="admin-wizard portal-wizard">
    <h1 class="wiz-title">Настройка организации</h1>
    <p class="wiz-desc">
      Пошагово задайте профиль организации: сегмент, контент, платформы, источники файлов и роли команды. В конце сохраните настройки.
    </p>
    <NAlert v-if="err" type="warning" :bordered="false" class="wiz-alert">{{ err }}</NAlert>
    <NSpin :show="loading">
      <NCard class="wiz-card" :bordered="false">
        <NSteps :current="current" class="wiz-steps">
          <NStep title="Профиль" description="Сегмент рынка" />
          <NStep title="Контент" description="Типы контента" />
          <NStep title="Платформы" description="Требования по типам контента" />
          <NStep title="Загруженные файлы" description="Загрузка и хранилища" />
          <NStep title="Команда" description="Пользователи и роли" />
          <NStep title="Обзор" description="Итог" />
        </NSteps>

        <!-- Шаг 1: сегмент — карточки как в HTML -->
        <div v-show="current === 1" class="step-body">
          <div class="sec-title">Сегмент рынка</div>
          <div class="sec-desc">Выберите сегмент — от него зависят рекомендуемые типы контента и платформы.</div>
          <div class="profiles">
            <button
              v-for="s in WIZARD_SEGMENTS"
              :key="s.id"
              type="button"
              class="profile"
              :class="{ on: form.segment === s.id }"
              @click="selectSegment(s.id)"
            >
              <span class="profile-check">{{ form.segment === s.id ? '✓' : '' }}</span>
              <span class="profile-icon">{{ s.ico }}</span>
              <div class="profile-name">{{ s.n }}</div>
              <div class="profile-desc">{{ s.d }}</div>
            </button>
          </div>
        </div>

        <!-- Шаг 2: 7 типов контента -->
        <div v-show="current === 2" class="step-body">
          <div class="sec-title">Типы контента</div>
          <div class="sec-desc">Отметьте типы контента, с которыми вы работаете. Рекомендации для выбранного сегмента подсвечены.</div>
          <div class="archive-note" :class="{ visible: form.content_types.includes('archive') }">
            <strong>Архивный контент (до 1991):</strong> учитывается исключение «историко-художественная ценность» по 436-ФЗ ч.2 ст.1.
          </div>
          <div class="ct-grid">
            <button
              v-for="t in WIZARD_CONTENT_TYPES"
              :key="t.id"
              type="button"
              class="ct-item"
              :class="{ on: form.content_types.includes(t.id) }"
              :style="form.content_types.includes(t.id) ? { borderColor: `${t.c}40` } : {}"
              @click="
                form.content_types = form.content_types.includes(t.id)
                  ? form.content_types.filter((x) => x !== t.id)
                  : [...form.content_types, t.id]
              "
            >
              <span class="ct-mark">{{ form.content_types.includes(t.id) ? '✓' : '' }}</span>
              <span class="ct-symbol" :style="{ color: t.c }">{{ t.sym }}</span>
              <div>
                <div class="ct-label">{{ t.n }}</div>
                <div v-if="recommendedCt.includes(t.id)" class="ct-rec">Рекомендован</div>
              </div>
            </button>
          </div>
        </div>

        <!-- Шаг 3: платформы + матрица (как renderPlatforms в HTML) -->
        <div v-show="current === 3" class="step-body">
          <div class="sec-title">Целевые платформы</div>
          <div class="sec-desc">Укажите целевые платформы вещания — ниже строится матрица соответствия для выбранных типов контента.</div>
          <div class="platforms">
            <button
              v-for="p in WIZARD_PLATFORMS"
              :key="p.id"
              type="button"
              class="platform"
              :class="{ on: form.platforms.includes(p.id) }"
              :style="form.platforms.includes(p.id) ? { borderColor: `${p.c}40` } : {}"
              @click="
                form.platforms = form.platforms.includes(p.id)
                  ? form.platforms.filter((x) => x !== p.id)
                  : [...form.platforms, p.id]
              "
            >
              <span class="plat-check">{{ form.platforms.includes(p.id) ? '✓' : '' }}</span>
              <div class="plat-name">
                {{ p.n }}
                <span v-if="recommendedPl.includes(p.id)" class="plat-rec">рек.</span>
              </div>
              <div class="plat-desc">{{ p.d }}</div>
              <div class="plat-npa">
                <span v-for="n in p.npa" :key="n" class="npa-tag">{{ n }}</span>
              </div>
            </button>
          </div>

          <div class="sec-title sub">Матрица соответствия</div>
          <div class="sec-desc small">Сводка по классам и выбранным типам: запрет, маркировка, проверка и особые случаи.</div>
          <div v-if="!activeTypes.length" class="matrix-empty">Выберите типы контента на шаге 2</div>
          <div v-else class="matrix-wrap">
            <table class="matrix">
              <thead>
                <tr>
                  <th>Подкласс</th>
                  <th v-for="t in activeTypes" :key="t.id" :style="{ color: t.c }">{{ t.sym }} {{ t.n }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="cls in COMPLIANCE_CLASSES" :key="cls.id">
                  <tr class="cls-header">
                    <td :colspan="activeTypes.length + 1">{{ cls.id }} · {{ cls.n }}</td>
                  </tr>
                  <tr
                    v-for="sub in cls.subs"
                    :key="sub.id"
                    :class="{ 'mx-diff': new Set(activeTypes.map((t) => cellVal(sub, t.id))).size > 1 }"
                  >
                    <td class="sub-cell">
                      <span class="sub-id">{{ sub.id }}</span>
                      {{ sub.n }}
                    </td>
                    <td v-for="t in activeTypes" :key="t.id" class="mx-cell">
                      <span
                        class="mx-icon"
                        :style="{
                          color: MATRIX_CELL_COLORS[cellVal(sub, t.id)] || MATRIX_CELL_COLORS.na,
                          opacity: cellVal(sub, t.id) === 'na' ? 0.35 : 1,
                        }"
                      >
                        {{ MATRIX_CELL_ICONS[cellVal(sub, t.id)] || '—' }}
                      </span>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          <div class="matrix-legend">
            <span>⛔ Запрет</span>
            <span>⚠️ Маркировка</span>
            <span class="leg-ok">✓ Проверка</span>
            <span class="leg-sp">◈ Особое</span>
            <span class="leg-ex">🛡 ИХЦ</span>
            <span>— Н/П</span>
          </div>
        </div>

        <!-- Шаг 4: источники -->
        <div v-show="current === 4" class="step-body">
          <div class="sec-title">Файлы и способы загрузки</div>
          <div class="sec-desc">
            Отметьте каналы, с которыми вы работаете. Подключение Яндекса и Google — через OAuth в
            «Настройках»; S3 — профили там же; фактический импорт — в «Загруженные файлы» → «Добавить
            файлы».
          </div>
          <div class="source-list">
            <div v-for="s in WIZARD_SOURCES" :key="s.id" class="source">
              <div class="source-ico">{{ s.ico }}</div>
              <div class="source-text">
                <div class="source-n">{{ s.n }}</div>
                <div class="source-d">{{ s.d }}</div>
              </div>
              <NSwitch
                :value="form.sources_enabled.includes(s.id)"
                @update:value="(v) => toggleSource(s.id, v)"
              />
            </div>
          </div>
        </div>

        <!-- Шаг 5: команда -->
        <div v-show="current === 5" class="step-body">
          <div class="sec-title">Команда и роли</div>
          <div class="sec-desc">
            Для вашего сегмента предусмотрены типовые роли портала. Учётные записи и назначение ролей — в разделе «Пользователи».
          </div>
          <div class="roles-grid">
            <div
              v-for="r in segmentRoles"
              :key="r.id"
              class="role-card"
              :style="{ borderTopColor: r.c }"
            >
              <div class="role-name">{{ r.n }}</div>
              <div class="role-desc">{{ r.d }}</div>
            </div>
          </div>
          <NButton type="primary" class="team-cta" @click="goUsers">Открыть «Пользователи»</NButton>
        </div>

        <!-- Шаг 6: обзор -->
        <div v-show="current === 6" class="step-body">
          <div class="sec-title">Обзор конфигурации</div>
          <div class="sec-desc">Проверьте выбранные параметры и нажмите «Сохранить», чтобы применить настройки.</div>
          <div class="summary">
            <div class="sum-card">
              <div class="sum-val">{{ overviewSeg?.ico }}</div>
              <div class="sum-label">{{ overviewSeg?.n }}</div>
            </div>
            <div class="sum-card">
              <div class="sum-val">{{ form.content_types.length }}</div>
              <div class="sum-label">типов контента</div>
            </div>
            <div class="sum-card">
              <div class="sum-val">{{ form.platforms.length }}</div>
              <div class="sum-label">платформ</div>
            </div>
            <div class="sum-card">
              <div class="sum-val">{{ form.sources_enabled.length }}</div>
              <div class="sum-label">источников</div>
            </div>
          </div>
          <div v-if="activeTypes.length" class="matrix-wrap overview-matrix">
            <table class="matrix">
              <thead>
                <tr>
                  <th>Подкласс</th>
                  <th v-for="t in activeTypes" :key="t.id" :style="{ color: t.c }">{{ t.sym }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="cls in COMPLIANCE_CLASSES.slice(0, 2)" :key="cls.id">
                  <tr class="cls-header">
                    <td :colspan="activeTypes.length + 1">{{ cls.id }} · {{ cls.n }}</td>
                  </tr>
                  <tr v-for="sub in cls.subs.slice(0, 3)" :key="sub.id">
                    <td class="sub-cell"><span class="sub-id">{{ sub.id }}</span> {{ sub.n }}</td>
                    <td v-for="t in activeTypes" :key="t.id" class="mx-cell">
                      {{ MATRIX_CELL_ICONS[cellVal(sub, t.id)] }}
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
            <p class="matrix-more">… полная матрица на шаге «Платформы»</p>
          </div>
        </div>

        <NSpace justify="space-between" class="wiz-nav">
          <NButton :disabled="current <= 1" @click="current--">← Назад</NButton>
          <NSpace>
            <NButton v-if="current < 6" type="primary" @click="current++">Далее →</NButton>
            <NButton v-else type="primary" :loading="saving" class="btn-save" @click="save">
              Сохранить конфигурацию
            </NButton>
          </NSpace>
        </NSpace>
      </NCard>
    </NSpin>
  </div>
</template>

<style scoped>
.portal-wizard {
  --wz-bl: #6898e8;
  --wz-gr: #2cd494;
  --wz-bg: var(--c-surface);
  --wz-bd: var(--c-border);
  --wz-t: var(--c-txt);
  --wz-t2: var(--c-txt-2);
  --wz-t3: var(--c-txt-3);
  --wz-th: var(--c-txt);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.wiz-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 8px;
}
.wiz-desc {
  font-size: 13px;
  color: var(--wz-t2);
  margin-bottom: 20px;
  line-height: 1.6;
}
.wiz-alert { margin-bottom: 14px; }
.wiz-card {
  background: var(--c-surface) !important;
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
}
.wiz-steps { margin-bottom: 28px; }
.step-body { min-height: 220px; margin-bottom: 8px; }
.sec-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--wz-th);
  margin-bottom: 8px;
}
.sec-title.sub { font-size: 14px; margin-top: 20px; }
.sec-desc {
  font-size: 13px;
  color: var(--wz-t2);
  margin-bottom: 20px;
  max-width: 680px;
  line-height: 1.65;
}
.sec-desc.small { font-size: 12px; margin-bottom: 12px; }

.profiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}
.profile {
  position: relative;
  padding: 20px 16px;
  border-radius: 14px;
  background: var(--c-surface-2);
  border: 2px solid var(--wz-bd);
  cursor: pointer;
  text-align: center;
  transition: all 0.25s;
  font: inherit;
  color: inherit;
}
.profile:hover { border-color: var(--wz-t3); transform: translateY(-1px); }
.profile.on {
  background: rgba(104, 152, 232, 0.06);
  border-color: rgba(104, 152, 232, 0.25);
  box-shadow: 0 2px 12px rgba(104, 152, 232, 0.12);
}
.profile-check {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1.5px solid var(--wz-bd);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.profile.on .profile-check {
  background: var(--wz-gr);
  border-color: var(--wz-gr);
  color: #fff;
}
.profile-icon { font-size: 28px; display: block; margin-bottom: 10px; }
.profile-name { font-size: 13px; font-weight: 600; }
.profile-desc { font-size: 9.5px; color: var(--wz-t3); margin-top: 6px; line-height: 1.45; }

.archive-note {
  display: none;
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(56, 192, 212, 0.06);
  border: 1px solid rgba(56, 192, 212, 0.12);
  font-size: 11px;
  color: var(--wz-t2);
  margin-bottom: 16px;
  line-height: 1.55;
}
.archive-note.visible { display: block; }
.archive-note strong { color: #38c0d4; }

.ct-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.ct-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1 1 140px;
  min-width: 120px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1.5px solid var(--wz-bd);
  background: var(--c-surface-2);
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  transition: all 0.22s;
}
.ct-item:hover { border-color: var(--wz-t3); }
.ct-item.on { background: rgba(104, 152, 232, 0.05); }
.ct-mark {
  width: 20px;
  height: 20px;
  border-radius: 7px;
  border: 1.5px solid var(--wz-bd);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ct-item.on .ct-mark {
  background: var(--wz-gr);
  border-color: var(--wz-gr);
  color: #fff;
}
.ct-symbol { font-size: 12px; font-weight: 700; width: 18px; text-align: center; flex-shrink: 0; }
.ct-label { font-size: 11px; font-weight: 500; }
.ct-rec { font-size: 8px; color: var(--wz-gr); margin-top: 2px; }

.platforms {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
  margin-bottom: 8px;
}
.platform {
  position: relative;
  padding: 16px;
  border-radius: 14px;
  background: var(--c-surface-2);
  border: 1.5px solid var(--wz-bd);
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  transition: all 0.22s;
}
.platform:hover { border-color: var(--wz-t3); }
.platform.on { background: rgba(104, 152, 232, 0.05); }
.plat-check {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 16px;
  height: 16px;
  border-radius: 5px;
  border: 1.5px solid var(--wz-bd);
  font-size: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.platform.on .plat-check {
  background: var(--wz-bl);
  border-color: var(--wz-bl);
  color: #fff;
}
.plat-name { font-size: 12px; font-weight: 600; padding-right: 22px; }
.plat-rec { font-size: 8px; color: var(--wz-gr); margin-left: 4px; }
.plat-desc { font-size: 9px; color: var(--wz-t3); margin-top: 4px; line-height: 1.45; }
.plat-npa { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 8px; }
.npa-tag {
  font-size: 7.5px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(104, 152, 232, 0.08);
  border: 1px solid rgba(104, 152, 232, 0.15);
  color: var(--wz-bl);
}

.matrix-empty { padding: 24px; text-align: center; color: var(--wz-t3); font-size: 13px; }
.matrix-wrap { overflow-x: auto; margin-top: 12px; }
.matrix {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 10px;
}
.matrix th {
  padding: 8px 6px;
  font-size: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--wz-t3);
  text-align: center;
  border-bottom: 1.5px solid var(--wz-bd);
  background: var(--c-bg);
}
.matrix th:first-child { text-align: left; min-width: 160px; }
.matrix td {
  padding: 7px 6px;
  text-align: center;
  border-bottom: 1px solid var(--wz-bd);
}
.matrix tr:hover td { background: var(--c-row-hover); }
.cls-header td {
  font-weight: 600;
  font-size: 11px;
  border-top: 1.5px solid var(--wz-bd);
  padding-top: 10px;
  background: var(--c-surface-2);
  text-align: left;
}
.sub-cell {
  text-align: left !important;
  font-size: 10px;
  padding-left: 16px !important;
}
.sub-id {
  color: var(--wz-bl);
  font-family: ui-monospace, monospace;
  font-weight: 600;
  margin-right: 4px;
}
.mx-diff td { background: rgba(104, 152, 232, 0.04); }
.mx-icon { font-size: 12px; }
.matrix-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
  font-size: 9px;
  color: var(--wz-t3);
}
.leg-ok { color: var(--wz-gr); }
.leg-sp { color: #8c7cd0; }
.leg-ex { color: #38c0d4; }

.source-list { display: flex; flex-direction: column; gap: 6px; }
.source {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--c-surface-2);
  border: 1px solid var(--wz-bd);
}
.source-ico {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  background: var(--c-surface);
  border: 1px solid var(--wz-bd);
  color: var(--wz-t2);
  flex-shrink: 0;
}
.source-text { flex: 1; min-width: 0; }
.source-n { font-size: 12px; font-weight: 600; }
.source-d { font-size: 9.5px; color: var(--wz-t3); margin-top: 2px; }

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  margin-bottom: 20px;
}
.role-card {
  padding: 14px;
  border-radius: 12px;
  background: var(--c-surface-2);
  border: 1px solid var(--wz-bd);
  border-top-width: 2px;
}
.role-name { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
.role-desc { font-size: 9.5px; color: var(--wz-t3); line-height: 1.4; }
.team-cta { margin-top: 8px; }

.summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}
.sum-card {
  padding: 18px;
  border-radius: 14px;
  background: var(--c-surface-2);
  border: 1px solid var(--wz-bd);
  text-align: center;
}
.sum-val { font-size: 24px; font-weight: 700; line-height: 1; }
.sum-label {
  font-size: 9px;
  color: var(--wz-t3);
  margin-top: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.overview-matrix { margin-top: 16px; }
.matrix-more { font-size: 11px; color: var(--wz-t3); margin-top: 8px; }

.wiz-nav {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--wz-bd);
}
.btn-save {
  border-color: rgba(44, 212, 148, 0.35) !important;
}

html[data-theme='light'] .portal-wizard .btn-save {
  background: linear-gradient(135deg, rgba(44, 212, 148, 0.15), rgba(44, 212, 148, 0.08)) !important;
}

/* Тёмная тема: явный светлый текст и читаемый фон (без «чёрного на тёмно-зелёном»). */
html[data-theme='dark'] .portal-wizard .btn-save {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.28), rgba(22, 163, 74, 0.18)) !important;
  box-shadow: 0 0 0 1px rgba(52, 211, 153, 0.35), 0 2px 12px rgba(0, 0, 0, 0.25);
}

/* Naive primary: в dark дефолтный --n-text-color может давать низкий контраст на кастомном фоне */
html[data-theme='light'] .portal-wizard .btn-save.n-button--primary-type {
  --n-text-color: #0a5c44 !important;
  --n-text-color-hover: #084a37 !important;
  --n-text-color-pressed: #063d2e !important;
  --n-text-color-focus: #0a5c44 !important;
  --n-text-color-disabled: rgba(10, 92, 68, 0.45) !important;
}

html[data-theme='dark'] .portal-wizard .btn-save.n-button--primary-type {
  --n-text-color: #ecfdf5 !important;
  --n-text-color-hover: #ffffff !important;
  --n-text-color-pressed: #d1fae5 !important;
  --n-text-color-focus: #ecfdf5 !important;
  --n-text-color-disabled: rgba(236, 253, 245, 0.45) !important;
  --n-border: 1px solid rgba(52, 211, 153, 0.45) !important;
  --n-border-hover: 1px solid rgba(52, 211, 153, 0.65) !important;
  --n-border-pressed: 1px solid rgba(52, 211, 153, 0.5) !important;
  --n-border-focus: 1px solid rgba(52, 211, 153, 0.65) !important;
}

/* Матрица и легенда: чуть выше контраст границ и подписей в тёмной теме */
html[data-theme='dark'] .portal-wizard .matrix th {
  color: var(--c-txt-2);
  border-bottom-color: rgba(148, 163, 184, 0.22);
  background: var(--c-surface-2);
}
html[data-theme='dark'] .portal-wizard .matrix td {
  border-bottom-color: rgba(148, 163, 184, 0.16);
}
html[data-theme='dark'] .portal-wizard .cls-header td {
  border-top-color: rgba(148, 163, 184, 0.22);
  color: var(--c-txt);
  background: rgba(255, 255, 255, 0.03);
}
html[data-theme='dark'] .portal-wizard .matrix-legend {
  color: var(--c-txt-2);
}
html[data-theme='dark'] .portal-wizard .sub-cell {
  color: var(--c-txt);
}
html[data-theme='dark'] .portal-wizard .wiz-nav {
  border-top-color: rgba(148, 163, 184, 0.2);
}
</style>
