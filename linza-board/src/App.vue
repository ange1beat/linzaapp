<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch, h, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ListOutline, SettingsOutline } from '@vicons/ionicons5'
import {
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider,
  NLoadingBarProvider,
  NButton,
  NIcon,
  NTooltip,
  NTag,
  NMenu,
  NAvatar,
  NBreadcrumb,
  NBreadcrumbItem,
  NSelect,
  darkTheme,
  ruRU,
  dateRuRU,
} from 'naive-ui'
import {
  DocumentTextOutline,
  AnalyticsOutline,
  FileTrayFullOutline,
  LockClosedOutline,
  BugOutline,
  PeopleOutline,
  InformationCircleOutline,
  HelpCircleOutline,
  LogOutOutline,
  SunnyOutline,
  MoonOutline,
  MenuOutline,
  CloseOutline,
  FolderOpenOutline,
} from '@vicons/ionicons5'
import { motion, MotionConfig, AnimatePresence } from 'motion-v'
import { useAuth } from './composables/useAuth.js'
import { useTheme } from './composables/useTheme.js'
import { landingPathForPortalRole } from './utils/portalLanding.js'
import { springLayout, pageEnter, pageActive, pageExit } from './motion/presets.js'
import RouteProgress from './components/RouteProgress.vue'

const route = useRoute()
const router = useRouter()

const {
  isAuthenticated,
  currentUser,
  logout,
  canManageUsers,
  canAccessSettings,
  fetchMe,
  getToken,
  switchPortalRole,
  portalRoles,
  activePortalRole,
} = useAuth()
const { theme, toggleTheme } = useTheme()

const naiveTheme = computed(() => (theme.value === 'dark' ? darkTheme : null))

const showShell = computed(() => isAuthenticated.value && route.path !== '/login')

const menuValue = computed(() => route.path)

/** Узкий экран: сайдбар выезжает поверх контента. */
const isNarrow = ref(false)
const sidebarOpen = ref(false)
let mqListener

function syncNarrow() {
  isNarrow.value = window.matchMedia('(max-width: 1023px)').matches
  if (!isNarrow.value) sidebarOpen.value = false
}

function onEscape(e) {
  if (e.key === 'Escape' && sidebarOpen.value && isNarrow.value) sidebarOpen.value = false
}

watch(
  () => route.fullPath,
  () => {
    if (isNarrow.value) sidebarOpen.value = false
  },
)

watch(
  [sidebarOpen, isNarrow],
  ([open, narrow]) => {
    if (typeof document === 'undefined') return
    document.body.style.overflow = narrow && open ? 'hidden' : ''
    if (open && narrow) {
      nextTick(() => {
        const first = document.querySelector('#app-sidebar .n-menu-item-content')
        if (first && typeof first.focus === 'function') first.focus()
      })
    }
  },
  { flush: 'post' },
)

const PORTAL_ROLE_SHORT = {
  administrator: 'Админ',
  operator: 'Оператор',
  lawyer: 'Юрист',
  chief_editor: 'Редактор',
}

async function onPortalRoleClick(r) {
  if (r === activePortalRole()) return
  const ok = await switchPortalRole(r)
  if (ok) router.push(landingPathForPortalRole(r))
}

const menuOptions = computed(() => {
  const helpGroup = {
    type: 'group',
    label: 'Справка',
    key: 'help',
    children: [
      { label: 'Инструкция', key: '/instructions', icon: renderIcon(HelpCircleOutline) },
      { label: 'О программе', key: '/about', icon: renderIcon(InformationCircleOutline) },
    ],
  }

  const ar = activePortalRole() || 'operator'

  if (ar === 'administrator') {
    const children = [
      { label: 'Настройка организации', key: '/admin/wizard', icon: renderIcon(SettingsOutline) },
      { label: 'Загруженные файлы', key: '/files', icon: renderIcon(FileTrayFullOutline) },
    ]
    if (canManageUsers()) {
      children.push({ label: 'Команда', key: '/users', icon: renderIcon(PeopleOutline) })
    }
    if (canAccessSettings()) {
      children.push({ label: 'Параметры доступа', key: '/settings/access', icon: renderIcon(LockClosedOutline) })
      if (currentUser.value?.role === 'superadmin' || currentUser.value?.role === 'admin') {
        children.push({ label: 'Ошибки', key: '/settings/error-tracking', icon: renderIcon(BugOutline) })
      }
    }
    return [{ type: 'group', label: 'Администратор', key: 'portal-adm', children }, helpGroup]
  }

  if (ar === 'operator') {
    return [
      {
        type: 'group',
        label: 'Файлы и очередь',
        key: 'op-ingest',
        children: [
          { label: 'Загруженные файлы', key: '/files', icon: renderIcon(FileTrayFullOutline) },
          { label: 'Очередь анализа', key: '/operator/queue', icon: renderIcon(ListOutline) },
        ],
      },
      {
        type: 'group',
        label: 'Отчёты',
        key: 'op-reports',
        children: [{ label: 'Результаты', key: '/results', icon: renderIcon(DocumentTextOutline) }],
      },
      helpGroup,
    ]
  }

  if (ar === 'lawyer') {
    return [
      {
        type: 'group',
        label: 'Проверка и отчёты',
        key: 'law',
        children: [
          { label: 'На рассмотрении', key: '/lawyer/review', icon: renderIcon(DocumentTextOutline) },
          { label: 'Отчёты', key: '/results', icon: renderIcon(FolderOpenOutline) },
        ],
      },
      helpGroup,
    ]
  }

  if (ar === 'chief_editor') {
    return [
      {
        type: 'group',
        label: 'Аналитика',
        key: 'editor',
        children: [
          { label: 'Дашборд', key: '/editor/dashboard', icon: renderIcon(AnalyticsOutline) },
          { label: 'Маркировка', key: '/editor/marking', icon: renderIcon(AnalyticsOutline) },
          { label: 'Команда', key: '/editor/team', icon: renderIcon(PeopleOutline) },
          { label: 'Результаты', key: '/results', icon: renderIcon(DocumentTextOutline) },
        ],
      },
      helpGroup,
    ]
  }

  return [
    {
      type: 'group',
      label: 'Файлы',
      key: 'wf-files',
      children: [{ label: 'Загруженные файлы', key: '/files', icon: renderIcon(FileTrayFullOutline) }],
    },
    {
      type: 'group',
      label: 'Отчёты',
      key: 'wf-reports',
      children: [{ label: 'Результаты', key: '/results', icon: renderIcon(DocumentTextOutline) }],
    },
    helpGroup,
  ]
})

const showRoleSwitcher = computed(() => portalRoles().length > 1)

const portalRoleSelectOptions = computed(() =>
  portalRoles().map((r) => ({ label: PORTAL_ROLE_SHORT[r] || r, value: r })),
)

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

function handleMenuUpdate(key) {
  if (isNarrow.value) sidebarOpen.value = false
  router.push(key)
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

/** Стартовая страница для текущей роли портала (логотип, крошка «Рабочий стол»). */
function goHome() {
  if (isNarrow.value) sidebarOpen.value = false
  const r = activePortalRole()
  router.push(landingPathForPortalRole(r || 'operator'))
}

function handleLogout() {
  logout()
  router.push('/login')
}

onMounted(() => {
  if (getToken()) fetchMe()
  syncNarrow()
  const mq = window.matchMedia('(max-width: 1023px)')
  mqListener = () => syncNarrow()
  mq.addEventListener('change', mqListener)
  window.addEventListener('keydown', onEscape)
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onEscape)
  if (mqListener) {
    window.matchMedia('(max-width: 1023px)').removeEventListener('change', mqListener)
  }
})
</script>

<template>
  <NConfigProvider
    :theme="naiveTheme"
    :theme-overrides="themeOverrides"
    :locale="ruRU"
    :date-locale="dateRuRU"
  >
    <NMessageProvider>
      <NDialogProvider>
        <NNotificationProvider>
          <NLoadingBarProvider>
            <RouteProgress />
            <MotionConfig :transition="springLayout" reducedMotion="user">
              <div class="app" :class="{ 'has-sidebar': showShell, 'is-narrow': isNarrow }">

                <div
                  v-if="showShell && isNarrow && sidebarOpen"
                  class="sidebar-backdrop"
                  aria-hidden="true"
                  @click="sidebarOpen = false"
                />

                <aside
                  v-if="showShell"
                  id="app-sidebar"
                  class="sidebar"
                  :class="{ 'sidebar--open': sidebarOpen && isNarrow, 'sidebar--overlay': isNarrow }"
                >
                  <NButton
                    quaternary
                    class="sidebar-logo-btn"
                    aria-label="Рабочий стол по роли"
                    @click="goHome"
                  >
                    <img src="./assets/linza-detector-logo.svg" alt="" class="logo-img" width="150" height="50" decoding="async" />
                  </NButton>

                  <NMenu
                    :value="menuValue"
                    :options="menuOptions"
                    :indent="20"
                    :root-indent="16"
                    @update:value="handleMenuUpdate"
                  />

                  <div class="sidebar-footer">
                    <div class="sidebar-user">
                      <NAvatar :size="28" round>
                        {{ (currentUser?.login ?? '?')[0].toUpperCase() }}
                      </NAvatar>
                      <div class="user-info">
                        <span class="user-name">{{ currentUser?.login ?? '' }}</span>
                        <NSelect
                          v-if="showRoleSwitcher"
                          class="sidebar-role-select"
                          size="tiny"
                          :value="activePortalRole()"
                          :options="portalRoleSelectOptions"
                          placeholder="Роль"
                          aria-label="Роль портала"
                          @update:value="onPortalRoleClick"
                        />
                        <NTag v-else :bordered="false" size="tiny" type="info">
                          {{ activePortalRole() ? (PORTAL_ROLE_SHORT[activePortalRole()] || activePortalRole()) : (currentUser?.role ?? '') }}
                        </NTag>
                      </div>
                    </div>
                    <NButton text type="error" @click="handleLogout" style="width:100%;justify-content:flex-start">
                      <template #icon><NIcon :component="LogOutOutline" /></template>
                      Выйти
                    </NButton>
                  </div>
                </aside>

                <main :class="showShell ? 'main-content' : 'main-full'">
                  <div v-if="showShell" class="content-header">
                    <div class="content-header-left">
                      <NButton
                        v-if="isNarrow"
                        quaternary
                        circle
                        class="menu-toggle"
                        :aria-expanded="sidebarOpen"
                        aria-controls="app-sidebar"
                        aria-label="Меню навигации"
                        @click="toggleSidebar"
                      >
                        <template #icon>
                          <NIcon :component="sidebarOpen ? CloseOutline : MenuOutline" />
                        </template>
                      </NButton>
                      <NBreadcrumb>
                        <NBreadcrumbItem>
                          <a href="#" class="bc-home" @click.prevent="goHome">Рабочий стол</a>
                        </NBreadcrumbItem>
                        <NBreadcrumbItem v-if="route.meta?.title">{{ route.meta.title }}</NBreadcrumbItem>
                      </NBreadcrumb>
                    </div>
                    <NTooltip>
                      <template #trigger>
                        <NButton quaternary circle @click="toggleTheme">
                          <template #icon>
                            <NIcon :component="theme === 'dark' ? SunnyOutline : MoonOutline" />
                          </template>
                        </NButton>
                      </template>
                      {{ theme === 'dark' ? 'Светлая тема' : 'Тёмная тема' }}
                    </NTooltip>
                  </div>

                  <router-view v-slot="{ Component }">
                    <AnimatePresence mode="wait" :initial="false">
                      <motion.div
                        v-if="Component"
                        :key="route.path"
                        class="route-page"
                        :initial="pageEnter"
                        :animate="pageActive"
                        :exit="pageExit"
                      >
                        <component :is="Component" />
                      </motion.div>
                    </AnimatePresence>
                  </router-view>
                </main>

              </div>
            </MotionConfig>
          </NLoadingBarProvider>
        </NNotificationProvider>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script>
const themeOverrides = {
  common: {
    primaryColor: '#4478ff',
    primaryColorHover: '#3464d8',
    primaryColorPressed: '#2256ee',
    borderRadius: '10px',
    borderRadiusSmall: '8px',
    fontFamily: "'DM Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    boxShadow1: '0 1px 2px rgba(15, 23, 42, 0.04)',
    boxShadow2: '0 4px 24px rgba(15, 23, 42, 0.06)',
  },
  Card: {
    borderRadius: '12px',
    paddingMedium: '18px',
    titleFontSizeSmall: '15px',
  },
  LoadingBar: {
    height: '3px',
  },
}
</script>

<style>
/* Типографика интерфейса (DM Sans + Inter) */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300..800;1,9..40,300..800&family=Inter:wght@300;400;500;600;700&display=swap');

:root,
html[data-theme="dark"] {
  --sidebar-w: 250px;
  --r-xs: 9px;
  --r-sm: 12px;
  --r-md: 14px;
  --r-lg: 18px;
  --r-xl: 22px;
  --r-2xl: 28px;
  --r-pill: 9999px;
  --c-sidebar: #141c28;
  --c-sidebar-hover: #1c2635;
  --c-sidebar-active: rgba(10, 111, 255, 0.14);
  --c-sidebar-border: rgba(148, 163, 184, 0.12);
  --c-bg: #0e131b;
  --c-surface: #161d2a;
  --c-surface-2: #1c2534;
  --c-border: rgba(148, 163, 184, 0.14);
  --c-blue: #3b82f6;
  --c-blue-dim: rgba(59, 130, 246, 0.14);
  --c-blue-hover: #2563eb;
  --c-teal: #2dd4bf;
  --c-teal-bg: rgba(45, 212, 191, 0.12);
  --c-txt: #f1f5f9;
  --c-txt-2: #94a3b8;
  --c-txt-3: #64748b;
  --c-err: #f87171;
  --c-err-bg: rgba(248, 113, 113, 0.1);
  --c-ok: #34d399;
  --c-ok-bg: rgba(52, 211, 153, 0.1);
  --c-warn: #fbbf24;
  --c-warn-bg: rgba(251, 191, 36, 0.1);
  --c-row-hover: rgba(255, 255, 255, 0.04);
  --c-modal-overlay: rgba(2, 6, 15, 0.58);
  --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.28);
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.32);
  --shadow-btn-primary: 0 4px 18px rgba(59, 130, 246, 0.4);
}

html[data-theme="light"] {
  --c-sidebar: #ffffff;
  --c-sidebar-hover: #f1f5f9;
  --c-sidebar-active: rgba(59, 130, 246, 0.12);
  --c-sidebar-border: #e8edf3;
  --c-bg: #eef2f7;
  --c-surface: #ffffff;
  --c-surface-2: #f5f8fc;
  --c-border: #e2e8f0;
  --c-blue: #2563eb;
  --c-blue-dim: rgba(37, 99, 235, 0.1);
  --c-blue-hover: #1d4ed8;
  --c-teal: #0d9488;
  --c-teal-bg: rgba(13, 148, 136, 0.1);
  --c-txt: #0f172a;
  --c-txt-2: #64748b;
  --c-txt-3: #94a3b8;
  --c-err: #dc2626;
  --c-err-bg: rgba(220, 38, 38, 0.08);
  --c-ok: #059669;
  --c-ok-bg: rgba(5, 150, 105, 0.1);
  --c-warn: #d97706;
  --c-warn-bg: rgba(217, 119, 6, 0.1);
  --c-row-hover: rgba(15, 23, 42, 0.035);
  --c-modal-overlay: rgba(15, 23, 42, 0.4);
  --shadow-soft: 0 2px 12px rgba(15, 23, 42, 0.06);
  --shadow-card: 0 8px 30px rgba(15, 23, 42, 0.08);
  --shadow-btn-primary: 0 4px 16px rgba(37, 99, 235, 0.35);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'DM Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--c-bg);
  color: var(--c-txt);
  font-size: 14px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

html[data-theme="light"] body {
  background: linear-gradient(168deg, #f1f5f9 0%, #eef2f7 42%, #e8edf4 100%);
  background-attachment: fixed;
}

html[data-theme="dark"] body {
  background: radial-gradient(ellipse 100% 60% at 50% -15%, rgba(59, 130, 246, 0.07), transparent 55%), var(--c-bg);
  background-attachment: fixed;
}

.app {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  min-width: 0;
  width: 100%;
}
.app.has-sidebar:not(.is-narrow) { padding-left: var(--sidebar-w); }
.app.has-sidebar.is-narrow { padding-left: 0; }

.sidebar-backdrop { display: none; }

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-w);
  max-width: min(var(--sidebar-w), 88vw);
  background: var(--c-sidebar);
  border-right: 1px solid var(--c-sidebar-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 1023px) {
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 99;
    background: var(--c-modal-overlay);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
  }

  .sidebar.sidebar--overlay {
    transform: translate3d(-100%, 0, 0);
    transition: transform 0.22s cubic-bezier(0.32, 0.72, 0, 1);
    will-change: transform;
  }

  .sidebar.sidebar--overlay.sidebar--open {
    transform: translate3d(0, 0, 0);
    box-shadow: var(--shadow-card);
  }
}

@media (min-width: 1024px) {
  .sidebar {
    transform: none !important;
    will-change: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sidebar.sidebar--overlay {
    transition: none;
  }
}

.sidebar-footer {
  padding: 12px 16px; border-top: 1px solid var(--c-sidebar-border);
  margin-top: auto;
  display: flex; flex-direction: column; gap: 10px;
}

.sidebar-user {
  display: flex; align-items: center; gap: 10px;
}

.user-info {
  display: flex; flex-direction: column; gap: 2px; min-width: 0;
}

.user-name {
  font-size: 13px; font-weight: 500; color: var(--c-txt);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 4px clamp(16px, 4vw, 32px) max(28px, env(safe-area-inset-bottom, 0px));
  min-height: 100vh;
  min-height: 100dvh;
}
.main-full { flex: 1; min-width: 0; min-height: 100vh; min-height: 100dvh; }
.route-page { width: 100%; max-width: 100%; }

.content-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 14px 0 16px; margin-bottom: 4px;
  border-bottom: 1px solid color-mix(in srgb, var(--c-border) 75%, transparent);
}

@media (max-width: 1023px) {
  .content-header {
    position: sticky;
    top: 0;
    z-index: 40;
    margin-top: -4px;
    padding-top: 12px;
    background: color-mix(in srgb, var(--c-bg) 88%, transparent);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }
}

.content-header-left {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.menu-toggle { flex-shrink: 0; }

.sidebar-role-select {
  width: 100%;
  margin-top: 6px;
}

a.bc-home {
  color: inherit;
  text-decoration: none;
  border-radius: 6px;
  padding: 2px 4px;
  margin: -2px -4px;
}
a.bc-home:hover {
  color: var(--c-blue);
}
a.bc-home:focus-visible {
  outline: 2px solid var(--c-blue);
  outline-offset: 2px;
}

.sidebar-logo-btn {
  width: 100% !important;
  height: auto !important;
  justify-content: flex-start !important;
  padding: 10px 16px 8px 18px !important;
  border-radius: var(--r-md) !important;
}
.sidebar-logo-btn:hover .logo-img { opacity: 1; }
.sidebar-logo-btn:focus-visible {
  outline: 2px solid var(--c-blue);
  outline-offset: 2px;
}
.logo-img {
  width: min(150px, 52vw);
  height: auto;
  display: block;
  object-fit: contain;
  opacity: 0.92;
  transition: opacity 0.2s ease;
}

/* Адаптив внутри страниц (дашборд редактора, маркировка, команда и т.д.) */
@media (max-width: 720px) {
  .route-page .hdr {
    flex-direction: column;
    align-items: stretch;
  }
  .route-page .hdr-actions {
    width: 100%;
    justify-content: space-between;
  }
  .route-page .seg {
    flex: 1;
    min-width: 0;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
}

@media (max-width: 560px) {
  .route-page .g.kpi-row,
  .route-page .charts {
    flex-direction: column;
  }
  .route-page .kpi,
  .route-page .c.wide {
    min-width: 0 !important;
    width: 100%;
  }
}

/* Legacy classes kept for existing components not yet migrated */
.linza-modal-enter-active, .linza-modal-leave-active { transition: opacity 0.22s ease; }
.linza-modal-enter-active .modal, .linza-modal-leave-active .modal,
.linza-modal-enter-active .player-container, .linza-modal-leave-active .player-container {
  transition: transform 0.26s cubic-bezier(0.34, 1.15, 0.64, 1), opacity 0.22s ease;
}
.linza-modal-enter-from, .linza-modal-leave-to { opacity: 0; }
.linza-modal-enter-from .modal, .linza-modal-leave-to .modal,
.linza-modal-enter-from .player-container, .linza-modal-leave-to .player-container {
  transform: scale(0.94) translateY(14px); opacity: 0;
}
.modal-overlay { position: fixed; inset: 0; background: var(--c-modal-overlay); display: flex; align-items: center; justify-content: center; z-index: 5000; }
.modal { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-xl); padding: 28px; width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-card); }
.modal h3 { font-size: 16px; margin-bottom: 20px; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 12px; color: var(--c-txt-2); margin-bottom: 4px; }
.field input, .field select, .field textarea { width: 100%; padding: 10px 14px; border-radius: var(--r-md); border: 1px solid var(--c-border); background: var(--c-surface-2); color: var(--c-txt); font-size: 13px; font-family: inherit; }
.field input:focus, .field select:focus { outline: none; border-color: var(--c-blue); }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px; }
.btn { padding: 9px 18px; border-radius: var(--r-md); font-size: 13px; border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-txt); cursor: pointer; font-family: inherit; transition: all 0.16s ease; display: inline-flex; align-items: center; gap: 6px; }
.btn:hover { background: var(--c-surface-2); }
.btn-primary { background: var(--c-blue); color: #fff; border-color: transparent; }
.btn-primary:hover { background: var(--c-blue-hover); border-color: transparent; }
.btn-sm { padding: 6px 12px; font-size: 12px; border-radius: var(--r-sm); }
.btn-danger { border-color: rgba(220,38,38,0.3); color: var(--c-err); }
.btn-danger:hover { background: var(--c-err-bg); }
.data-table { width: 100%; border-collapse: collapse; background: var(--c-surface); border-radius: var(--r-lg); overflow: hidden; border: 1px solid var(--c-border); }
.data-table th { padding: 10px 14px; text-align: left; font-size: 12px; font-weight: 500; color: var(--c-txt-2); background: var(--c-surface-2); border-bottom: 1px solid var(--c-border); }
.data-table td { padding: 10px 14px; font-size: 13px; border-bottom: 1px solid var(--c-border); }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: var(--c-row-hover); }
.badge { display: inline-block; padding: 3px 10px; border-radius: var(--r-pill); font-size: 11px; font-weight: 500; }
.badge-ok { background: var(--c-ok-bg); color: var(--c-ok); }
.badge-err { background: var(--c-err-bg); color: var(--c-err); }
.badge-warn { background: var(--c-warn-bg); color: var(--c-warn); }
.badge-blue { background: var(--c-blue-dim); color: var(--c-blue); }
.icon-btn { background: none; border: none; cursor: pointer; color: var(--c-txt-2); padding: 6px; border-radius: var(--r-sm); transition: all 0.15s; }
.icon-btn:hover { color: var(--c-txt); background: var(--c-surface-2); }
.empty-state { text-align: center; padding: 40px; color: var(--c-txt-3); font-size: 13px; }
.alert { padding: 10px 16px; border-radius: var(--r-md); font-size: 12px; margin-bottom: 14px; }
.alert-error { background: var(--c-err-bg); color: var(--c-err); }
.alert-ok { background: var(--c-ok-bg); color: var(--c-ok); }
.search-input { padding: 9px 14px; border-radius: var(--r-md); border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-txt); font-size: 13px; font-family: inherit; min-width: 240px; }
.search-input:focus { outline: none; border-color: var(--c-blue); }
.search-input::placeholder { color: var(--c-txt-3); }
.page-title { font-size: 19px; font-weight: 600; margin-bottom: 18px; letter-spacing: -0.02em; }
.page-toolbar { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; flex-wrap: wrap; }
</style>
