<script setup>
import { ref, onMounted, computed, h } from 'vue'
import { NCard, NDataTable, NEmpty, NProgress, NSpin, NTag } from 'naive-ui'
import { useStorageQuotas } from '../composables/useStorageQuotas.js'

const { quotas, usage, loading, fetchQuotas, fetchUsage } = useStorageQuotas()

onMounted(async () => {
  await Promise.all([fetchQuotas(), fetchUsage()])
})

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}

const scopeLabels = { tenant: 'Организация', team: 'Команда', user: 'Пользователь' }

const columns = [
  {
    title: 'Тип',
    key: 'scope_type',
    render: (row) => h(NTag, { type: 'info', size: 'small' }, { default: () => scopeLabels[row.scope_type] || row.scope_type }),
    width: 140,
  },
  { title: 'ID', key: 'scope_id', width: 80 },
  {
    title: 'Квота',
    key: 'quota_bytes',
    render: (row) => formatBytes(row.quota_bytes),
    width: 120,
  },
  {
    title: 'Использовано',
    key: 'used_bytes',
    render: (row) => formatBytes(row.used_bytes),
    width: 120,
  },
  {
    title: '%',
    key: 'percentage',
    render: (row) => {
      const pct = row.quota_bytes > 0 ? Math.round((row.used_bytes / row.quota_bytes) * 100) : 0
      return h(NProgress, { type: 'line', percentage: pct, status: pct > 90 ? 'error' : pct > 70 ? 'warning' : 'default' })
    },
    width: 180,
  },
]
</script>

<template>
  <div>
    <h2 class="page-title">Квоты хранилища</h2>

    <NCard v-if="usage" style="margin-bottom: 16px">
      <h3 style="margin: 0 0 12px; font-size: 14px; color: var(--c-txt-2)">Моё использование</h3>
      <div v-if="usage.user" style="margin-bottom: 8px">
        <span style="font-size: 12px; color: var(--c-txt-2)">Личная:</span>
        {{ formatBytes(usage.user.used_bytes) }} / {{ formatBytes(usage.user.quota_bytes) }}
      </div>
      <div v-if="usage.team" style="margin-bottom: 8px">
        <span style="font-size: 12px; color: var(--c-txt-2)">Команда:</span>
        {{ formatBytes(usage.team.used_bytes) }} / {{ formatBytes(usage.team.quota_bytes) }}
      </div>
      <div v-if="usage.tenant" style="margin-bottom: 8px">
        <span style="font-size: 12px; color: var(--c-txt-2)">Организация:</span>
        {{ formatBytes(usage.tenant.used_bytes) }} / {{ formatBytes(usage.tenant.quota_bytes) }}
      </div>
      <div v-if="!usage.user && !usage.team && !usage.tenant" style="color: var(--c-txt-3)">
        Квоты не настроены
      </div>
    </NCard>

    <NCard>
      <NSpin :show="loading">
        <NDataTable v-if="quotas.length" :columns="columns" :data="quotas" :bordered="false" />
        <NEmpty v-else description="Нет квот" />
      </NSpin>
    </NCard>
  </div>
</template>
