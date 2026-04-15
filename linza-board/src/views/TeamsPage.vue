<script setup>
import { ref, onMounted } from 'vue'
import {
  NButton, NCard, NDataTable, NInput, NModal, NSpace, NSpin, NEmpty,
} from 'naive-ui'
import { useRouter } from 'vue-router'
import { useTeams } from '../composables/useTeams.js'

const router = useRouter()
const { teams, loading, fetchTeams, createTeam, deleteTeam } = useTeams()

const showCreate = ref(false)
const newName = ref('')
const creating = ref(false)

onMounted(() => fetchTeams())

const columns = [
  { title: 'Название', key: 'name' },
  { title: 'Участников', key: 'member_count', width: 120 },
  {
    title: 'Создана',
    key: 'created_at',
    render: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString('ru') : '—',
    width: 140,
  },
  {
    title: '',
    key: 'actions',
    width: 200,
    render: (row) =>
      h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', onClick: () => router.push(`/teams/${row.id}`) }, { default: () => 'Открыть' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.id) }, { default: () => 'Удалить' }),
        ],
      }),
  },
]

import { h } from 'vue'

async function handleCreate() {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    await createTeam(newName.value.trim())
    newName.value = ''
    showCreate.value = false
  } finally { creating.value = false }
}

async function handleDelete(id) {
  await deleteTeam(id)
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 class="page-title">Команды</h2>
      <NButton type="primary" @click="showCreate = true">Создать команду</NButton>
    </div>

    <NCard>
      <NSpin :show="loading">
        <NDataTable v-if="teams.length" :columns="columns" :data="teams" :bordered="false" />
        <NEmpty v-else description="Нет команд" />
      </NSpin>
    </NCard>

    <NModal v-model:show="showCreate" preset="dialog" title="Новая команда">
      <NInput v-model:value="newName" placeholder="Название команды" @keyup.enter="handleCreate" />
      <template #action>
        <NSpace>
          <NButton @click="showCreate = false">Отмена</NButton>
          <NButton type="primary" :loading="creating" @click="handleCreate">Создать</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>
