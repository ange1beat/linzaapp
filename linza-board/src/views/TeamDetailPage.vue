<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NDataTable, NEmpty, NSpin, NTag } from 'naive-ui'
import { useRoute } from 'vue-router'
import { useTeams } from '../composables/useTeams.js'

const route = useRoute()
const { fetchTeamMembers } = useTeams()

const teamId = Number(route.params.id)
const members = ref([])
const loading = ref(true)

const columns = [
  {
    title: 'Имя',
    key: 'name',
    render: (row) => `${row.first_name} ${row.last_name}`,
  },
  { title: 'Email', key: 'email' },
  {
    title: 'Роль',
    key: 'role',
    render: (row) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.role }),
  },
]

onMounted(async () => {
  try {
    members.value = await fetchTeamMembers(teamId)
  } finally { loading.value = false }
})
</script>

<template>
  <div>
    <h2 class="page-title">Участники команды</h2>
    <NCard>
      <NSpin :show="loading">
        <NDataTable v-if="members.length" :columns="columns" :data="members" :bordered="false" />
        <NEmpty v-else description="Нет участников" />
      </NSpin>
    </NCard>
  </div>
</template>
