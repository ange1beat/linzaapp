import { ref } from 'vue'
import { useAuth } from './useAuth'

export function useTeams() {
  const teams = ref([])
  const loading = ref(false)
  const error = ref('')
  const { getToken } = useAuth()

  const headers = () => ({
    Authorization: `Bearer ${getToken()}`,
    'Content-Type': 'application/json',
  })

  async function fetchTeams() {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch('/api/teams/', { headers: headers() })
      if (res.ok) teams.value = await res.json()
      else error.value = 'Ошибка загрузки команд'
    } catch { error.value = 'Ошибка соединения' }
    finally { loading.value = false }
  }

  async function createTeam(name) {
    const res = await fetch('/api/teams/', {
      method: 'POST', headers: headers(),
      body: JSON.stringify({ name }),
    })
    if (!res.ok) throw new Error('Ошибка создания команды')
    await fetchTeams()
  }

  async function deleteTeam(id) {
    await fetch(`/api/teams/${id}`, { method: 'DELETE', headers: headers() })
    await fetchTeams()
  }

  async function fetchTeamMembers(teamId) {
    const res = await fetch(`/api/teams/${teamId}/members`, { headers: headers() })
    if (res.ok) return res.json()
    return []
  }

  async function addTeamMembers(teamId, userIds) {
    await fetch(`/api/teams/${teamId}/members`, {
      method: 'POST', headers: headers(),
      body: JSON.stringify({ user_ids: userIds }),
    })
  }

  async function removeTeamMember(teamId, userId) {
    await fetch(`/api/teams/${teamId}/members/${userId}`, {
      method: 'DELETE', headers: headers(),
    })
  }

  return {
    teams, loading, error,
    fetchTeams, createTeam, deleteTeam,
    fetchTeamMembers, addTeamMembers, removeTeamMember,
  }
}
