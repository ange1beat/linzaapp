<script setup>
import { ref, onMounted, h } from 'vue'
import {
  NButton, NCard, NDataTable, NEmpty, NInput, NModal, NSpace, NSpin, NTag,
} from 'naive-ui'
import { useProjects } from '../composables/useProjects.js'

const { projects, total, loading, fetchProjects, createProject, deleteProject, toggleFavorite } = useProjects()

const search = ref('')
const showCreate = ref(false)
const newName = ref('')
const creating = ref(false)

onMounted(() => fetchProjects())

const columns = [
  { title: 'Название', key: 'name' },
  {
    title: 'Избранное',
    key: 'is_favorite',
    width: 100,
    render: (row) => h(
      NButton,
      { text: true, onClick: () => handleToggleFav(row) },
      { default: () => row.is_favorite ? '★' : '☆' },
    ),
  },
  {
    title: 'Создан',
    key: 'created_at',
    render: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString('ru') : '—',
    width: 140,
  },
  {
    title: '',
    key: 'actions',
    width: 120,
    render: (row) => h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.id) }, { default: () => 'Удалить' }),
  },
]

async function handleSearch() {
  await fetchProjects(search.value)
}

async function handleCreate() {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    await createProject(newName.value.trim())
    newName.value = ''
    showCreate.value = false
    await fetchProjects(search.value)
  } finally { creating.value = false }
}

async function handleDelete(id) {
  await deleteProject(id)
  await fetchProjects(search.value)
}

async function handleToggleFav(row) {
  const result = await toggleFavorite(row.id)
  if (result) row.is_favorite = result.is_favorite
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 class="page-title">Проекты</h2>
      <NButton type="primary" @click="showCreate = true">Создать проект</NButton>
    </div>

    <NCard style="margin-bottom: 16px">
      <NSpace>
        <NInput v-model:value="search" placeholder="Поиск проектов..." style="width: 300px" @keyup.enter="handleSearch" />
        <NButton @click="handleSearch">Найти</NButton>
      </NSpace>
    </NCard>

    <NCard>
      <NSpin :show="loading">
        <NDataTable v-if="projects.length" :columns="columns" :data="projects" :bordered="false" />
        <NEmpty v-else description="Нет проектов" />
      </NSpin>
      <div v-if="total > 0" style="margin-top: 8px; color: var(--c-txt-2); font-size: 12px">
        Всего: {{ total }}
      </div>
    </NCard>

    <NModal v-model:show="showCreate" preset="dialog" title="Новый проект">
      <NInput v-model:value="newName" placeholder="Название проекта" @keyup.enter="handleCreate" />
      <template #action>
        <NSpace>
          <NButton @click="showCreate = false">Отмена</NButton>
          <NButton type="primary" :loading="creating" @click="handleCreate">Создать</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>
