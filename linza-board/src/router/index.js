/**
 * Vue Router configuration for Linza Board SPA.
 *
 * Defines all application routes with authentication and role guards.
 * Тяжёлые страницы подгружаются лениво — меньше начальный бандл и быстрее первый экран.
 */

import { createRouter, createWebHistory } from 'vue-router'
import { landingPathForPortalRole } from '../utils/portalLanding.js'

const routes = [
  { path: '/login', component: () => import('../views/LoginPage.vue'), meta: { public: true } },

  {
    path: '/',
    redirect: (to) => ({ path: '/results', query: to.query }),
  },
  { path: '/files', component: () => import('../views/FilesPage.vue'), meta: { requiresAuth: true, title: 'Загруженные файлы' } },
  { path: '/results', component: () => import('../views/ResultsPage.vue'), meta: { requiresAuth: true, title: 'Результаты анализа' } },
  {
    path: '/operator/queue',
    component: () => import('../views/QueuePage.vue'),
    meta: { requiresAuth: true, portalRoles: ['operator'], title: 'Очередь анализа' },
  },
  {
    path: '/lawyer/review',
    component: () => import('../views/LawyerReviewPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['lawyer'], title: 'На рассмотрении' },
  },
  {
    path: '/editor/dashboard',
    component: () => import('../views/EditorDashboardPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['chief_editor'], title: 'Дашборд' },
  },
  {
    path: '/editor/team',
    component: () => import('../views/EditorTeamPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['chief_editor'], title: 'Команда' },
  },
  {
    path: '/editor/marking',
    component: () => import('../views/EditorMarkingPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['chief_editor'], title: 'Маркировка' },
  },
  {
    path: '/admin/wizard',
    component: () => import('../views/AdminWizardPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['administrator'], title: 'Настройка организации' },
  },

  { path: '/users', component: () => import('../views/UsersPage.vue'), meta: { requiresAuth: true, managerOnly: true, title: 'Пользователи' } },
  {
    path: '/settings/access',
    component: () => import('../views/AccessParamsPage.vue'),
    meta: { requiresAuth: true, managerOnly: true, title: 'Параметры доступа' },
  },
  { path: '/settings/sources', redirect: '/files' },
  { path: '/settings/system-storage', redirect: '/files' },
  { path: '/settings/storage', redirect: '/files' },
  {
    path: '/settings/error-tracking',
    component: () => import('../views/ErrorTrackingPage.vue'),
    meta: { requiresAuth: true, managerOnly: true, title: 'Отслеживание ошибок' },
  },

  {
    path: '/teams',
    component: () => import('../views/TeamsPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['administrator'], title: 'Команды' },
  },
  {
    path: '/teams/:id',
    component: () => import('../views/TeamDetailPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['administrator'], title: 'Команда' },
  },
  {
    path: '/projects',
    component: () => import('../views/ProjectsPage.vue'),
    meta: { requiresAuth: true, title: 'Проекты' },
  },
  {
    path: '/storage-quotas',
    component: () => import('../views/StorageQuotasPage.vue'),
    meta: { requiresAuth: true, portalRoles: ['administrator'], title: 'Квоты хранилища' },
  },

  { path: '/instructions', component: () => import('../views/InstructionPage.vue'), meta: { requiresAuth: true, title: 'Инструкция' } },
  { path: '/about', component: () => import('../views/AboutPage.vue'), meta: { requiresAuth: true, title: 'О программе' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, saved) {
    if (saved) return saved
    return { top: 0, left: 0, behavior: 'auto' }
  },
})

function queryFlagOne(q, key) {
  const v = q?.[key]
  if (v == null || v === '') return false
  if (Array.isArray(v)) return v.some((x) => String(x) === '1')
  return String(v) === '1'
}

router.beforeEach(async (to) => {
  const token = localStorage.getItem('linza_token')
  if (token && to.path !== '/files' && queryFlagOne(to.query, 'yandex_connected')) {
    return { path: '/files', query: { yandex_connected: '1' }, replace: true }
  }
  if (token && to.path !== '/files' && to.query.yandex_error != null && to.query.yandex_error !== '') {
    return {
      path: '/files',
      query: { yandex_error: String(to.query.yandex_error) },
      replace: true,
    }
  }
  if (token && to.path !== '/files' && queryFlagOne(to.query, 'google_connected')) {
    return { path: '/files', query: { google_connected: '1' }, replace: true }
  }
  if (token && to.path !== '/files' && to.query.google_error != null && to.query.google_error !== '') {
    return {
      path: '/files',
      query: { google_error: String(to.query.google_error) },
      replace: true,
    }
  }
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.path === '/login' && token) {
    try {
      const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) {
        const user = await res.json()
        return landingPathForPortalRole(user.active_role || 'operator')
      }
    } catch { /* */ }
    return landingPathForPortalRole('operator')
  }
  if (to.meta.managerOnly && token) {
    try {
      const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) {
        const user = await res.json()
        const ok =
          user.role === 'superadmin' ||
          user.role === 'admin' ||
          user.active_role === 'administrator'
        if (!ok) return landingPathForPortalRole(user.active_role || 'operator')
      }
    } catch { /* */ }
  }
  if (to.meta.portalRoles?.length && token) {
    try {
      const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) {
        const user = await res.json()
        if (!to.meta.portalRoles.includes(user.active_role)) {
          return landingPathForPortalRole(user.active_role || 'operator')
        }
      }
    } catch { /* */ }
  }
})

export default router
