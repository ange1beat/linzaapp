import { ref } from 'vue'
import { useAuth } from './useAuth'

export function useStorageQuotas() {
  const quotas = ref([])
  const usage = ref(null)
  const loading = ref(false)
  const { getToken } = useAuth()

  const headers = () => ({
    Authorization: `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  })

  async function fetchQuotas(scopeType) {
    loading.value = true
    try {
      const params = scopeType ? `?scope_type=${scopeType}` : ''
      const res = await fetch(`/api/storage/quotas${params}`, { headers: headers() })
      if (res.ok) quotas.value = await res.json()
    } catch { /* ignore */ }
    finally { loading.value = false }
  }

  async function fetchUsage() {
    try {
      const res = await fetch('/api/storage/usage', { headers: headers() })
      if (res.ok) usage.value = await res.json()
    } catch { /* ignore */ }
  }

  async function setQuota(scopeType, scopeId, quotaBytes) {
    const res = await fetch('/api/storage/quotas', {
      method: 'POST', headers: headers(),
      body: JSON.stringify({ scope_type: scopeType, scope_id: scopeId, quota_bytes: quotaBytes }),
    })
    if (!res.ok) throw new Error('Ошибка установки квоты')
    await fetchQuotas()
  }

  return { quotas, usage, loading, fetchQuotas, fetchUsage, setQuota }
}
