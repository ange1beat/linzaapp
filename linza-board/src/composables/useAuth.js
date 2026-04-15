import { ref } from 'vue'

const TOKEN_KEY = 'linza_token'

const isAuthenticated = ref(!!localStorage.getItem(TOKEN_KEY))
const currentUser = ref(null)
const authError = ref('')

export function useAuth() {
  function getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  async function login(login, password) {
    authError.value = ''
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        authError.value = data.detail || 'Неверный логин или пароль'
        return false
      }
      const { access_token } = await res.json()
      localStorage.setItem(TOKEN_KEY, access_token)
      isAuthenticated.value = true
      await fetchMe()
      return true
    } catch {
      authError.value = 'Ошибка соединения с сервером'
      return false
    }
  }

  async function fetchMe() {
    const token = getToken()
    if (!token) return
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        currentUser.value = await res.json()
      } else {
        logout()
      }
    } catch {
      // ignore
    }
  }

  async function switchPortalRole(activeRole) {
    const token = getToken()
    if (!token) return false
    try {
      const res = await fetch('/api/auth/switch-role', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ active_role: activeRole }),
      })
      if (!res.ok) return false
      const { access_token } = await res.json()
      localStorage.setItem(TOKEN_KEY, access_token)
      await fetchMe()
      return true
    } catch {
      return false
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    isAuthenticated.value = false
    currentUser.value = null
  }

  function canManageUsers() {
    const u = currentUser.value
    if (!u) return false
    if (u.role === 'superadmin' || u.role === 'admin') return true
    return u.active_role === 'administrator'
  }

  function isSuperAdmin() {
    return currentUser.value?.role === 'superadmin'
  }

  function canAccessSettings() {
    const u = currentUser.value
    if (!u) return false
    if (u.role === 'superadmin' || u.role === 'admin') return true
    return u.active_role === 'administrator'
  }

  function canManageTeams() {
    return canManageUsers()
  }

  function canManageStorage() {
    return canManageUsers()
  }

  /** Роли портала (переключение контекста в интерфейсе). */
  function portalRoles() {
    return currentUser.value?.portal_roles ?? []
  }

  function activePortalRole() {
    return currentUser.value?.active_role ?? null
  }

  function hasPortalRole(role) {
    return portalRoles().includes(role)
  }

  function currentTenantId() {
    return currentUser.value?.tenant_id ?? null
  }

  function currentTeamId() {
    return currentUser.value?.team_id ?? null
  }

  function storageInfo() {
    return {
      quotaBytes: currentUser.value?.storage_quota_bytes ?? 0,
      usedBytes: currentUser.value?.storage_used_bytes ?? 0,
    }
  }

  return {
    isAuthenticated,
    currentUser,
    authError,
    login,
    logout,
    fetchMe,
    getToken,
    switchPortalRole,
    canManageUsers,
    isSuperAdmin,
    canAccessSettings,
    canManageTeams,
    canManageStorage,
    portalRoles,
    activePortalRole,
    hasPortalRole,
    currentTenantId,
    currentTeamId,
    storageInfo,
  }
}
