import { ref } from 'vue'
import { useAuth } from './useAuth.js'

const profiles = ref([])
const loading = ref(false)
const error = ref('')

export function useStorage() {
  const { getToken } = useAuth()

  function headers() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    }
  }

  async function fetchProfiles() {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch('/api/settings/storage', { headers: headers() })
      if (res.ok) {
        profiles.value = await res.json()
      } else {
        error.value = 'Ошибка загрузки профилей'
      }
    } catch {
      error.value = 'Ошибка соединения'
    } finally {
      loading.value = false
    }
  }

  async function createProfile(data) {
    const res = await fetch('/api/settings/storage', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || 'Ошибка создания профиля')
    }
    await fetchProfiles()
    return await res.json()
  }

  async function updateProfile(id, data) {
    const res = await fetch(`/api/settings/storage/${id}`, {
      method: 'PUT',
      headers: headers(),
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || 'Ошибка обновления')
    }
    await fetchProfiles()
  }

  async function deleteProfile(id) {
    const res = await fetch(`/api/settings/storage/${id}`, {
      method: 'DELETE',
      headers: headers(),
    })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || 'Ошибка удаления')
    }
    await fetchProfiles()
  }

  async function activateProfile(id) {
    const res = await fetch(`/api/settings/storage/${id}/activate`, {
      method: 'POST',
      headers: headers(),
    })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || 'Ошибка активации')
    }
    await fetchProfiles()
  }

  async function testConnection(id) {
    const res = await fetch(`/api/settings/storage/${id}/test`, {
      method: 'POST',
      headers: headers(),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      throw new Error(data.detail || 'Ошибка подключения')
    }
    return data
  }

  return { profiles, loading, error, fetchProfiles, createProfile, updateProfile, deleteProfile, activateProfile, testConnection }
}
