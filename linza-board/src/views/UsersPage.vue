<script setup>
import { ref, onMounted, computed, h } from 'vue'
import {
  NButton,
  NCard,
  NInput,
  NSelect,
  NTag,
  NModal,
  NSpace,
  NGrid,
  NGi,
  NAvatar,
  NEmpty,
  NSpin,
  NAlert,
  NIcon,
  NPopconfirm,
  NCheckboxGroup,
  NCheckbox,
  NDivider,
} from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline, RefreshOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'

const { currentUser, getToken } = useAuth()

const users = ref([])
const loading = ref(false)
const showCreate = ref(false)
const editingUser = ref(null)
const formError = ref('')
const formLoading = ref(false)
const searchQuery = ref('')

const portalRoleOptions = [
  { label: 'Администратор', value: 'administrator' },
  { label: 'Оператор вещания', value: 'operator' },
  { label: 'Юрист', value: 'lawyer' },
  { label: 'Главный редактор', value: 'chief_editor' },
]

const createForm = ref({
  first_name: '', last_name: '', login: '', password: '', email: '', role: 'user', portal_roles: [],
})
const editForm = ref({ first_name: '', last_name: '', email: '', role: '', password: '', portal_roles: [] })

const isSuperadmin = computed(() => currentUser.value?.role === 'superadmin')

function portalRoleLabel(v) {
  return portalRoleOptions.find((o) => o.value === v)?.label || v
}

const filteredUsers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter((u) => {
    const prText = (u.portal_roles || []).map((pr) => portalRoleLabel(pr).toLowerCase()).join(' ')
    return (
      u.first_name.toLowerCase().includes(q) ||
      u.last_name.toLowerCase().includes(q) ||
      u.login.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      roleLabel(u.role).toLowerCase().includes(q) ||
      prText.includes(q)
    )
  })
})

const stats = computed(() => {
  const total = users.value.length
  const admins = users.value.filter(u => u.role === 'admin' || u.role === 'superadmin').length
  const regular = users.value.filter(u => u.role === 'user').length
  return { total, admins, regular }
})

function authHeaders() {
  return { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' }
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await fetch('/api/users/', { headers: { Authorization: `Bearer ${getToken()}` } })
    if (res.ok) users.value = await res.json()
  } catch {} finally { loading.value = false }
}

function openCreate() {
  createForm.value = {
    first_name: '', last_name: '', login: '', password: '', email: '', role: 'user', portal_roles: [],
  }
  formError.value = ''
  showCreate.value = true
}

async function submitCreate() {
  formError.value = ''
  formLoading.value = true
  try {
    const body = { ...createForm.value }
    if (!body.portal_roles?.length) delete body.portal_roles
    const res = await fetch('/api/users/', { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      formError.value = d.detail || 'Ошибка создания'
      return
    }
    showCreate.value = false
    await fetchUsers()
  } catch { formError.value = 'Ошибка соединения' } finally { formLoading.value = false }
}

function openEdit(u) {
  editingUser.value = u.id
  editForm.value = {
    first_name: u.first_name,
    last_name: u.last_name,
    email: u.email,
    role: u.role,
    password: '',
    portal_roles: Array.isArray(u.portal_roles) ? [...u.portal_roles] : [],
  }
  formError.value = ''
}

function cancelEdit() { editingUser.value = null; formError.value = '' }

async function submitEdit(id) {
  formError.value = ''
  formLoading.value = true
  const body = {}
  const orig = users.value.find(u => u.id === id)
  if (editForm.value.first_name !== orig?.first_name) body.first_name = editForm.value.first_name
  if (editForm.value.last_name !== orig?.last_name) body.last_name = editForm.value.last_name
  if (editForm.value.email !== orig?.email) body.email = editForm.value.email
  if (editForm.value.role !== orig?.role) body.role = editForm.value.role
  if (editForm.value.password) body.password = editForm.value.password
  const origPr = JSON.stringify(orig?.portal_roles || [])
  const newPr = JSON.stringify(editForm.value.portal_roles || [])
  if (origPr !== newPr) body.portal_roles = editForm.value.portal_roles
  if (!Object.keys(body).length) { editingUser.value = null; formLoading.value = false; return }
  try {
    const res = await fetch(`/api/users/${id}`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(body) })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      formError.value = d.detail || 'Ошибка сохранения'
      return
    }
    editingUser.value = null
    await fetchUsers()
  } catch { formError.value = 'Ошибка соединения' } finally { formLoading.value = false }
}

async function deleteUser(id) {
  try {
    await fetch(`/api/users/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${getToken()}` } })
    await fetchUsers()
  } catch {}
}

const roleLabel = (r) => ({ superadmin: 'Суперадмин', admin: 'Администратор', user: 'Пользователь' })[r] || r

const roleTagType = (r) => ({ superadmin: 'error', admin: 'info', user: 'success' })[r] || 'default'

const roleOptions = computed(() => {
  const opts = [{ label: 'Пользователь', value: 'user' }]
  if (isSuperadmin.value) opts.push({ label: 'Администратор', value: 'admin' })
  return opts
})

function initials(u) {
  return ((u.first_name?.[0] || '') + (u.last_name?.[0] || '')).toUpperCase() || '?'
}

function avatarColor(role) {
  return { superadmin: '#a855f7', admin: '#3b82f6', user: '#34d399' }[role] || '#64748b'
}

onMounted(fetchUsers)
</script>

<template>
  <div class="users">
    <header class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">Пользователи</h1>
        <p class="pg-d">
          Команда организации: системные роли и роли портала (оператор, юрист, редактор и т.д.).
        </p>
      </div>
      <div class="hdr-actions">
        <NButton quaternary circle :loading="loading" aria-label="Обновить список" @click="fetchUsers">
          <template #icon><NIcon :component="RefreshOutline" /></template>
        </NButton>
        <NButton type="primary" @click="openCreate">
          <template #icon><NIcon :component="AddOutline" /></template>
          Новый пользователь
        </NButton>
      </div>
    </header>

    <NCard class="workspace-card" :bordered="true" size="small">
      <div class="workspace-inner">
        <div class="kpi-strip" role="group" aria-label="Сводка по пользователям">
          <div class="kpi-cell">
            <span class="kpi-val">{{ stats.total }}</span>
            <span class="kpi-lbl">Всего</span>
          </div>
          <div class="kpi-rule" aria-hidden="true" />
          <div class="kpi-cell">
            <span class="kpi-val kpi-val-accent">{{ stats.admins }}</span>
            <span class="kpi-lbl">Админы</span>
          </div>
          <div class="kpi-rule" aria-hidden="true" />
          <div class="kpi-cell">
            <span class="kpi-val">{{ stats.regular }}</span>
            <span class="kpi-lbl">Без админ-прав</span>
          </div>
        </div>

        <NDivider class="workspace-divider" />

        <div class="filter-block">
          <label class="filter-label" for="users-search">Поиск в списке</label>
          <div class="filter-row">
            <NInput
              id="users-search"
              v-model:value="searchQuery"
              class="search-full"
              placeholder="Имя, фамилия, логин, email или роль портала…"
              clearable
            />
            <NTag v-if="searchQuery.trim()" round :bordered="false" size="medium" type="info" class="filter-count">
              {{ filteredUsers.length }} из {{ users.length }}
            </NTag>
          </div>
        </div>
      </div>
    </NCard>

    <div class="list-head">
      <h2 class="list-title">Участники</h2>
      <span v-if="!loading" class="list-meta">Показано: {{ filteredUsers.length }}</span>
    </div>

    <NSpin :show="loading">
      <NEmpty v-if="!loading && filteredUsers.length === 0" :description="searchQuery ? 'Ничего не найдено' : 'Нет пользователей'" />

      <NGrid v-else :cols="'1 600:2'" :x-gap="14" :y-gap="14">
        <NGi v-for="u in filteredUsers" :key="u.id">
          <NCard size="small" :bordered="true" hoverable>
            <template v-if="editingUser !== u.id">
              <NSpace align="center" :size="12" class="card-head">
                <NAvatar :size="40" round :style="{ backgroundColor: avatarColor(u.role) }">
                  {{ initials(u) }}
                </NAvatar>
                <div class="card-meta">
                  <div class="card-name">{{ u.first_name }} {{ u.last_name }}</div>
                  <div class="card-login">@{{ u.login }}</div>
                </div>
                <NTag :type="roleTagType(u.role)" round size="small">{{ roleLabel(u.role) }}</NTag>
              </NSpace>
              <div class="card-email">
                {{ u.email }}
              </div>
              <div v-if="u.portal_roles?.length" class="card-portal-tags">
                <NTag v-for="pr in u.portal_roles" :key="pr" size="tiny" round type="success">
                  {{ portalRoleLabel(pr) }}
                </NTag>
              </div>
              <NSpace v-if="u.role !== 'superadmin' || isSuperadmin" :size="8" class="card-actions">
                <NButton v-if="u.role !== 'superadmin'" size="small" @click="openEdit(u)">
                  <template #icon><NIcon :component="CreateOutline" /></template>
                  Изменить
                </NButton>
                <NPopconfirm v-if="u.role !== 'superadmin'" @positive-click="deleteUser(u.id)">
                  <template #trigger>
                    <NButton size="small" type="error" ghost>
                      <template #icon><NIcon :component="TrashOutline" /></template>
                      Удалить
                    </NButton>
                  </template>
                  Точно удалить пользователя?
                </NPopconfirm>
              </NSpace>
            </template>

            <template v-else>
              <form @submit.prevent="submitEdit(u.id)">
                <NSpace vertical :size="10">
                  <NSpace :size="10">
                    <NInput v-model:value="editForm.first_name" placeholder="Имя" size="small" />
                    <NInput v-model:value="editForm.last_name" placeholder="Фамилия" size="small" />
                  </NSpace>
                  <NInput v-model:value="editForm.email" placeholder="Email" size="small" />
                  <NSpace :size="10">
                    <NSelect v-model:value="editForm.role" class="role-select" :options="roleOptions" size="small" :disabled="u.role === 'superadmin'" />
                    <NInput v-model:value="editForm.password" type="password" placeholder="Новый пароль" size="small" />
                  </NSpace>
                  <div class="field-hint">Роли портала</div>
                  <NCheckboxGroup v-model:value="editForm.portal_roles">
                    <NSpace vertical :size="4">
                      <NCheckbox v-for="opt in portalRoleOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
                    </NSpace>
                  </NCheckboxGroup>
                  <NAlert v-if="formError" type="error" :bordered="false" class="form-alert">{{ formError }}</NAlert>
                  <NSpace justify="end">
                    <NButton size="small" @click="cancelEdit">Отмена</NButton>
                    <NButton size="small" type="primary" attr-type="submit" :loading="formLoading">Сохранить</NButton>
                  </NSpace>
                </NSpace>
              </form>
            </template>
          </NCard>
        </NGi>
      </NGrid>
    </NSpin>

    <NModal v-model:show="showCreate" preset="card" title="Новый пользователь" :style="{ maxWidth: '480px' }">
      <form @submit.prevent="submitCreate">
        <NSpace vertical :size="12">
          <NSpace :size="10">
            <NInput v-model:value="createForm.first_name" placeholder="Имя" />
            <NInput v-model:value="createForm.last_name" placeholder="Фамилия" />
          </NSpace>
          <NInput v-model:value="createForm.login" placeholder="Логин" />
          <NInput v-model:value="createForm.password" type="password" placeholder="Пароль (мин. 4 символа)" />
          <NInput v-model:value="createForm.email" placeholder="Email" />
          <NSelect v-model:value="createForm.role" :options="roleOptions" />
          <div class="field-hint">Роли портала — необязательно; иначе доступ по системной роли</div>
          <NCheckboxGroup v-model:value="createForm.portal_roles">
            <NSpace vertical :size="4">
              <NCheckbox v-for="opt in portalRoleOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
            </NSpace>
          </NCheckboxGroup>
          <NAlert v-if="formError" type="error" :bordered="false">{{ formError }}</NAlert>
          <NSpace justify="end">
            <NButton @click="showCreate = false">Отмена</NButton>
            <NButton type="primary" attr-type="submit" :loading="formLoading">Создать</NButton>
          </NSpace>
        </NSpace>
      </form>
    </NModal>
  </div>
</template>

<style scoped>
.users {
  max-width: 1040px;
  width: 100%;
  margin: 0 auto;
  padding-bottom: 32px;
}

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.hdr-txt {
  min-width: 0;
  flex: 1;
}
.pg-t {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 8px;
  color: var(--c-txt);
}
.pg-d {
  font-size: 14px;
  line-height: 1.55;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 58ch;
}
.hdr-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.workspace-card {
  margin-bottom: 28px;
}

.workspace-card :deep(.n-card__content) {
  padding-top: 16px;
  padding-bottom: 16px;
}

.workspace-inner {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.kpi-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  border-radius: var(--r-md);
  border: 1px solid var(--c-border);
  background: var(--c-surface-2);
  overflow: hidden;
}

.kpi-cell {
  flex: 1 1 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 14px 12px;
  text-align: center;
}

.kpi-val {
  font-size: 1.5rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  color: var(--c-txt);
  line-height: 1.1;
}

.kpi-val-accent {
  color: var(--c-blue);
}

.kpi-lbl {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--c-txt-3);
}

.kpi-rule {
  width: 1px;
  align-self: stretch;
  min-height: 48px;
  background: var(--c-border);
  flex-shrink: 0;
}

@media (max-width: 520px) {
  .kpi-rule {
    display: none;
  }
  .kpi-cell {
    flex: 1 1 33%;
    border-bottom: 1px solid var(--c-border);
    padding: 12px 8px;
  }
  .kpi-cell:last-child {
    border-bottom: none;
  }
}

.workspace-divider {
  margin: 18px 0 !important;
}

.filter-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--c-txt-2);
  letter-spacing: 0.02em;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.search-full {
  flex: 1 1 200px;
  min-width: 0;
}

.filter-count {
  flex-shrink: 0;
}

.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px 16px;
  margin-bottom: 14px;
}

.list-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-txt);
  letter-spacing: -0.02em;
}

.list-meta {
  font-size: 13px;
  color: var(--c-txt-3);
  font-variant-numeric: tabular-nums;
}

.field-hint {
  font-size: 11px;
  color: var(--c-txt-3);
  line-height: 1.4;
}

.role-select {
  min-width: 160px;
}

.form-alert {
  font-size: 12px;
}

.card-head {
  margin-bottom: 10px;
}
.card-meta {
  flex: 1;
  min-width: 0;
}
.card-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--c-txt);
}
.card-login {
  font-size: 12px;
  color: var(--c-txt-3);
  font-family: ui-monospace, monospace;
}
.card-email {
  font-size: 12px;
  color: var(--c-txt-2);
  padding: 8px 0;
  border-top: 1px solid var(--c-border);
}
.card-portal-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.card-actions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--c-border);
}
</style>
