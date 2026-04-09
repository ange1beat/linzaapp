<script setup>
import { ref, h, onMounted } from 'vue'
import {
  NButton, NDataTable, NModal, NInput, NSpace, NEmpty, NSpin, NAlert, NIcon,
  NPopconfirm,
  useMessage,
} from 'naive-ui'
import { AddOutline, CreateOutline, TrashOutline, RefreshOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'

const { getToken } = useAuth()
const message = useMessage()

const items = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingId = ref(null)
const formError = ref('')

const form = ref({ workspace: '', domain: '', login: '', password: '' })

function headers() {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` }
}

async function fetchItems() {
  loading.value = true
  try {
    const res = await fetch('/api/settings/access', { headers: headers() })
    if (res.ok) items.value = await res.json()
  } catch {
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = { workspace: '', domain: '', login: '', password: '' }
  editingId.value = null
  formError.value = ''
}

function openCreate() {
  resetForm()
  showModal.value = true
}

function openEdit(item) {
  form.value = {
    workspace: item.workspace || '',
    domain: item.domain || '',
    login: item.login || '',
    password: '',
  }
  editingId.value = item.id
  formError.value = ''
  showModal.value = true
}

async function handleSubmit() {
  formError.value = ''
  try {
    const data = { ...form.value }
    if (!data.password) delete data.password
    if (editingId.value) {
      const res = await fetch(`/api/settings/access/${editingId.value}`, {
        method: 'PUT',
        headers: headers(),
        body: JSON.stringify(data),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.detail || 'Error')
      }
    } else {
      const res = await fetch('/api/settings/access', {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(data),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.detail || 'Error')
      }
    }
    showModal.value = false
    resetForm()
    await fetchItems()
  } catch (e) {
    formError.value = e.message
  }
}

async function handleDelete(id) {
  try {
    const res = await fetch(`/api/settings/access/${id}`, { method: 'DELETE', headers: headers() })
    if (!res.ok) throw new Error('Не удалось удалить')
    await fetchItems()
    message.success('Учётные данные удалены')
  } catch (e) {
    message.error(e.message || 'Ошибка удаления')
  }
}

const columns = [
  { title: 'Название', key: 'workspace', render: (row) => row.workspace || row.name || '—' },
  { title: 'Домен', key: 'domain', render: (row) => row.domain || '—' },
  { title: 'Логин', key: 'login', render: (row) => row.login || '—' },
  {
    title: 'Действия',
    key: 'actions',
    width: 120,
    render: (row) =>
      h(NSpace, { size: 4 }, () => [
        h(
          NButton,
          { quaternary: true, circle: true, size: 'small', onClick: () => openEdit(row) },
          { icon: () => h(NIcon, { component: CreateOutline }) },
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete(row.id) },
          {
            trigger: () =>
              h(
                NButton,
                { quaternary: true, circle: true, size: 'small', type: 'error' },
                { icon: () => h(NIcon, { component: TrashOutline }) },
              ),
            default: () => 'Удалить учётные данные?',
          },
        ),
      ]),
  },
]

onMounted(fetchItems)
</script>

<template>
  <div class="access-page">
    <div class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">Параметры доступа</h1>
        <p class="pg-d">Учётные данные для внешних сервисов и интеграций организации.</p>
      </div>
      <div class="hdr-actions">
        <NButton quaternary circle :loading="loading" aria-label="Обновить список" @click="fetchItems">
          <template #icon><NIcon :component="RefreshOutline" /></template>
        </NButton>
        <NButton type="primary" @click="openCreate">
          <template #icon><NIcon :component="AddOutline" /></template>
          Добавить
        </NButton>
      </div>
    </div>

    <NSpin :show="loading">
      <div v-if="items.length || loading" class="table-wrap">
        <NDataTable
          :columns="columns"
          :data="items"
          :row-key="(r) => r.id"
          :bordered="true"
          :single-line="false"
          striped
          size="small"
          :scroll-x="720"
        />
      </div>
      <NEmpty v-else class="empty-state" description="Нет учётных данных" />
    </NSpin>

    <NModal
      v-model:show="showModal"
      preset="card"
      :title="editingId ? 'Редактирование' : 'Новые учётные данные'"
      :style="{ maxWidth: '460px' }"
    >
      <NAlert v-if="formError" type="error" :bordered="false" class="modal-alert">{{ formError }}</NAlert>
      <form @submit.prevent="handleSubmit">
        <NSpace vertical :size="12">
          <NInput v-model:value="form.workspace" placeholder="Рабочее пространство" />
          <NInput v-model:value="form.domain" placeholder="Домен (example.com)" />
          <NInput v-model:value="form.login" placeholder="Логин" />
          <NInput v-model:value="form.password" type="password" placeholder="Пароль (пусто = не менять)" />
          <NSpace justify="end">
            <NButton @click="showModal = false">Назад</NButton>
            <NButton type="primary" attr-type="submit">Сохранить</NButton>
          </NSpace>
        </NSpace>
      </form>
    </NModal>
  </div>
</template>

<style scoped>
.access-page {
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
}

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.hdr-txt {
  min-width: 0;
  flex: 1;
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
  max-width: 52ch;
}
.hdr-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: var(--r-sm);
}

.empty-state {
  padding: 48px 0;
}

.modal-alert {
  margin-bottom: 12px;
}
</style>
