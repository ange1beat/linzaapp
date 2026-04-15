import { ref } from 'vue'
import { useAuth } from './useAuth'

export function useProjects() {
  const projects = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')
  const { getToken } = useAuth()

  const headers = () => ({
    Authorization: `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  })

  async function fetchProjects(name = '', page = 1, pageSize = 10) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams({ PageSize: pageSize, PageNumber: page })
      if (name) params.set('name', name)
      const res = await fetch(`/api/projects/?${params}`, { headers: headers() })
      if (res.ok) {
        const data = await res.json()
        projects.value = data.projects
        total.value = data.total
      } else { error.value = 'Ошибка загрузки проектов' }
    } catch { error.value = 'Ошибка соединения' }
    finally { loading.value = false }
  }

  async function createProject(name) {
    const res = await fetch('/api/projects/', {
      method: 'POST', headers: headers(),
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error('Ошибка создания проекта')
    return res.json()
  }

  async function deleteProject(id) {
    await fetch(`/api/projects/${id}`, { method: 'DELETE', headers: headers() })
  }

  async function toggleFavorite(id) {
    const res = await fetch(`/api/projects/${id}/favorite`, {
      method: 'POST', headers: headers(),
    })
    if (res.ok) return res.json()
  }

  return {
    projects, total, loading, error,
    fetchProjects, createProject, deleteProject, toggleFavorite,
  }
}
