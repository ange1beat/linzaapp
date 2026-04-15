<!--
  ErrorTrackingPage.vue — Error Tracking settings page.

  Displays centralized error tracking dashboard for admin/superadmin users.
  Features:
  - Statistics cards: total errors, errors in last hour, breakdown by service
  - Filters: filter by service name and severity level
  - Error table: sortable list with expandable rows for traceback details
  - GitHub Issue submission: opens pre-filled issue in BigDataQueen/Linza-debug
  - Manual error report: modal form to create a new error report manually
  - Clear errors: bulk delete with optional service filter

  Uses useErrorTracking composable for all API interactions.
  Follows the dark theme design system (CSS variables from App.vue).
-->

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useErrorTracking } from '../composables/useErrorTracking.js'

// --- Composable: provides reactive state and API methods ---
const {
  errors,       // ref<Array> — list of error records
  total,        // ref<number> — total count matching filters
  stats,        // ref<Object> — aggregate statistics
  loading,      // ref<boolean> — loading state
  fetchErrors,
  fetchStats,
  clearErrors,
  submitToGithub,
  createManualError,
  buildGitHubIssueUrl,
} = useErrorTracking()

// --- Local state for filters ---
/** Selected service name filter (empty string = all services) */
const filterService = ref('')

/** Selected severity level filter (empty string = all levels) */
const filterSeverity = ref('')

/** ID of the currently expanded row (shows traceback details) */
const expandedId = ref(null)

// --- Modal state for manual error report form ---
/** Controls visibility of the manual error report modal */
const showReportModal = ref(false)

/** Form data for the manual error report modal */
const reportForm = ref({
  service: 'linza-board',
  severity: 'error',
  category: 'ui',
  message: '',
  description: '',
  submit_github: false,
})

/** Error message displayed in the modal form */
const reportError = ref('')

/** Success message displayed in the modal form */
const reportSuccess = ref('')

/** Loading state for the modal submit button */
const reportLoading = ref(false)

// --- Computed: unique service names for the filter dropdown ---
/** Extract unique service names from stats.by_service for the dropdown */
const serviceOptions = computed(() => Object.keys(stats.value.by_service || {}))

// --- Methods ---

/**
 * Apply current filters and reload the error list.
 * Called when filter dropdowns change or on manual refresh.
 */
async function applyFilters() {
  await fetchErrors({
    service: filterService.value || undefined,
    severity: filterSeverity.value || undefined,
  })
}

/** Полное обновление: статистика и список с учётом фильтров. */
async function refreshAll() {
  await fetchStats()
  await applyFilters()
}

/**
 * Toggle expanded state of a table row.
 * Shows/hides traceback and additional details for the selected error.
 * @param {number} id - error record ID to toggle
 */
function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

/**
 * Handle "Submit to GitHub" button click for an existing error.
 * 1. Builds a pre-filled GitHub new issue URL from error data
 * 2. Opens the URL in a new browser tab
 * 3. Marks the error as 'submitted' in the backend
 * @param {Object} error - error record object
 */
async function handleSubmitToGithub(error) {
  const url = buildGitHubIssueUrl(error)
  window.open(url, '_blank')
  await submitToGithub(error.id, url)
}

/**
 * Handle "Clear errors" button click.
 * Deletes all errors (or filtered by service) and refreshes the view.
 */
async function handleClear() {
  await clearErrors(filterService.value || undefined)
  await fetchStats()
}

/**
 * Open the manual error report modal and reset form state.
 */
function openReportModal() {
  reportForm.value = {
    service: 'linza-board',
    severity: 'error',
    category: 'ui',
    message: '',
    description: '',
    submit_github: false,
  }
  reportError.value = ''
  reportSuccess.value = ''
  showReportModal.value = true
}

/**
 * Close the manual error report modal.
 */
function closeReportModal() {
  showReportModal.value = false
}

/**
 * Submit the manual error report form.
 *
 * Calls createManualError() from the composable.
 * If submit_github is checked, opens the GitHub issue URL in a new tab.
 * On success, shows a success message and refreshes the error list.
 */
async function handleSubmitReport() {
  // Validate required field
  if (!reportForm.value.message.trim()) {
    reportError.value = 'Укажите сообщение об ошибке'
    return
  }

  reportError.value = ''
  reportSuccess.value = ''
  reportLoading.value = true

  try {
    const result = await createManualError(reportForm.value)

    // If GitHub submission was requested, open the pre-filled issue URL
    if (result.github_issue_url) {
      window.open(result.github_issue_url, '_blank')
      // Mark as submitted in the backend
      await submitToGithub(result.id, result.github_issue_url)
    }

    reportSuccess.value = 'Отчёт об ошибке успешно создан' +
      (result.github_issue_url ? ' и отправлен в GitHub' : '')

    // Auto-close modal after 1.5 seconds
    setTimeout(() => {
      showReportModal.value = false
    }, 1500)
  } catch (e) {
    reportError.value = e.message || 'Ошибка при создании отчёта'
  } finally {
    reportLoading.value = false
  }
}

/**
 * Map severity level to CSS badge class for visual styling.
 * @param {string} severity - error severity level
 * @returns {string} CSS class name for the badge
 */
function severityBadge(severity) {
  const map = {
    critical: 'badge-err',
    error: 'badge-err',
    warning: 'badge-warn',
    info: 'badge-blue',
  }
  return map[severity] || 'badge-blue'
}

/**
 * Format ISO timestamp to a human-readable local datetime string.
 * @param {string} iso - ISO 8601 timestamp from the API
 * @returns {string} formatted date string (DD.MM.YYYY HH:MM:SS)
 */
function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

// --- Lifecycle: load data on mount ---
onMounted(async () => {
  await fetchStats()
  await fetchErrors()
})
</script>

<template>
  <div class="error-tracking-page">
    <div class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">Отслеживание ошибок</h1>
        <p class="pg-d">Сводка по сервисам, фильтры и отправка в GitHub Issues.</p>
      </div>
    </div>

    <!-- Statistics cards row -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">Всего ошибок</div>
      </div>
      <div class="stat-card">
        <div class="stat-value stat-warn">{{ stats.last_hour }}</div>
        <div class="stat-label">За последний час</div>
      </div>
      <div v-for="(count, svc) in stats.by_service" :key="svc" class="stat-card">
        <div class="stat-value stat-blue">{{ count }}</div>
        <div class="stat-label">{{ svc }}</div>
      </div>
    </div>

    <!-- Toolbar: filters and actions -->
    <div class="page-toolbar et-toolbar">
      <!-- Service filter -->
      <select v-model="filterService" class="search-input et-filter-svc" @change="applyFilters">
        <option value="">Все сервисы</option>
        <option v-for="svc in serviceOptions" :key="svc" :value="svc">{{ svc }}</option>
      </select>
      <!-- Severity filter -->
      <select v-model="filterSeverity" class="search-input et-filter-sev" @change="applyFilters">
        <option value="">Все уровни</option>
        <option value="critical">Critical</option>
        <option value="error">Error</option>
        <option value="warning">Warning</option>
        <option value="info">Info</option>
      </select>
      <!-- Refresh -->
      <button class="btn" :disabled="loading" @click="refreshAll">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/><path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/></svg>
        Обновить
      </button>
      <!-- Create manual error report button -->
      <button class="btn btn-primary" @click="openReportModal">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg>
        Создать отчёт
      </button>
      <!-- Clear errors -->
      <button class="btn btn-danger" @click="handleClear">
        <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H5.5l1-1h3l1 1H14a1 1 0 0 1 1 1v1z"/></svg>
        Очистить
      </button>
      <!-- Total count -->
      <span class="badge badge-blue et-total">Всего: {{ total }}</span>
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="empty-state">Загрузка...</div>

    <!-- Empty state -->
    <div v-else-if="errors.length === 0" class="empty-state">
      Ошибок не обнаружено
    </div>

    <!-- Errors table -->
    <div v-else class="table-scroll">
    <table class="data-table">
      <thead>
        <tr>
          <th class="col-date">Дата</th>
          <th class="col-svc">Сервис</th>
          <th class="col-sev">Уровень</th>
          <th>Сообщение</th>
          <th class="col-status">Статус</th>
          <th class="col-actions">Действия</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="error in errors" :key="error.id">
          <!-- Main error row -->
          <tr class="row-click" @click="toggleExpand(error.id)">
            <td>{{ formatDate(error.created_at) }}</td>
            <td><span class="badge badge-blue">{{ error.service }}</span></td>
            <td><span class="badge" :class="severityBadge(error.severity)">{{ error.severity }}</span></td>
            <td class="msg-cell">{{ error.message }}</td>
            <td>
              <span v-if="error.status === 'submitted'" class="badge badge-ok">Отправлено</span>
              <span v-else class="badge badge-muted">Новая</span>
            </td>
            <td @click.stop>
              <button
                v-if="error.status !== 'submitted'"
                class="btn btn-sm btn-primary"
                @click="handleSubmitToGithub(error)"
                title="Отправить как Issue в GitHub"
              >
                GitHub Issue
              </button>
              <a
                v-else-if="error.github_issue_url"
                :href="error.github_issue_url"
                target="_blank"
                class="btn btn-sm"
                @click.stop
              >
                Посмотреть
              </a>
            </td>
          </tr>
          <!-- Expanded details row -->
          <tr v-if="expandedId === error.id" class="expanded-row">
            <td colspan="6">
              <div class="error-details">
                <div v-if="error.endpoint" class="detail-item">
                  <span class="detail-label">Эндпоинт:</span>
                  <code>{{ error.method }} {{ error.endpoint }}</code>
                </div>
                <div v-if="error.status_code" class="detail-item">
                  <span class="detail-label">Статус код:</span>
                  <code>{{ error.status_code }}</code>
                </div>
                <div v-if="error.request_id" class="detail-item">
                  <span class="detail-label">Request ID:</span>
                  <code>{{ error.request_id }}</code>
                </div>
                <div v-if="error.category" class="detail-item">
                  <span class="detail-label">Категория:</span>
                  <code>{{ error.category }}</code>
                </div>
                <div v-if="error.traceback" class="detail-item">
                  <span class="detail-label">Traceback:</span>
                  <pre class="traceback-block">{{ error.traceback }}</pre>
                </div>
                <div v-if="error.extra" class="detail-item">
                  <span class="detail-label">Дополнительно:</span>
                  <pre class="traceback-block">{{ error.extra }}</pre>
                </div>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    </div>

    <!-- ============================================================= -->
    <!-- Modal: Manual Error Report Form                                -->
    <!-- Allows the user to describe an error they encountered and     -->
    <!-- optionally submit it as a GitHub Issue to Linza-debug repo.   -->
    <!-- ============================================================= -->
    <Transition name="linza-modal">
      <div v-if="showReportModal" class="modal-overlay" @click.self="closeReportModal">
        <div class="modal modal-report">
        <h3>Создать отчёт об ошибке</h3>

        <!-- Error/success alerts -->
        <div v-if="reportError" class="alert alert-error">{{ reportError }}</div>
        <div v-if="reportSuccess" class="alert alert-ok">{{ reportSuccess }}</div>

        <!-- Service selector -->
        <div class="field">
          <label>Сервис</label>
          <select v-model="reportForm.service">
            <option value="linza-board">linza-board</option>
            <option value="linza-vpleer">linza-vpleer</option>
            <option value="linza-storage-service">linza-storage-service</option>
            <option value="linza-analytics">linza-analytics</option>
          </select>
        </div>

        <!-- Two-column row: severity + category -->
        <div class="field-row">
          <!-- Severity selector -->
          <div class="field field-grow">
            <label>Серьёзность</label>
            <select v-model="reportForm.severity">
              <option value="critical">Critical</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>
          <!-- Category selector -->
          <div class="field field-grow">
            <label>Категория</label>
            <select v-model="reportForm.category">
              <option value="ui">Интерфейс (UI)</option>
              <option value="api">API</option>
              <option value="storage">Хранилище (Storage)</option>
              <option value="auth">Авторизация (Auth)</option>
              <option value="player">Видеоплеер (Player)</option>
              <option value="analytics">Аналитика (Analytics)</option>
              <option value="network">Сеть (Network)</option>
            </select>
          </div>
        </div>

        <!-- Error message (required) -->
        <div class="field">
          <label>Краткое описание ошибки *</label>
          <input
            v-model="reportForm.message"
            type="text"
            placeholder="Например: Не загружается страница аналитики"
          />
        </div>

        <!-- Detailed description (optional) -->
        <div class="field">
          <label>Подробное описание / шаги воспроизведения</label>
          <textarea
            v-model="reportForm.description"
            rows="5"
            placeholder="Опишите что произошло, какие действия привели к ошибке..."
          ></textarea>
        </div>

        <!-- Checkbox: immediately submit to GitHub -->
        <div class="field field-checkbox">
          <input
            id="submit-github-check"
            v-model="reportForm.submit_github"
            type="checkbox"
            class="github-check"
          />
          <label for="submit-github-check" class="github-check-label">
            Сразу отправить в GitHub Issues (Linza-debug)
          </label>
        </div>

        <!-- Form actions -->
        <div class="form-actions">
          <button class="btn" @click="closeReportModal">Отмена</button>
          <button
            class="btn btn-primary"
            :disabled="reportLoading"
            @click="handleSubmitReport"
          >
            {{ reportLoading ? 'Создание...' : 'Создать отчёт' }}
          </button>
        </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.error-tracking-page {
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
}

.hdr {
  margin-bottom: 18px;
}
.hdr-txt {
  min-width: 0;
}
.pg-t {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 6px;
  color: var(--c-txt);
}
.pg-d {
  font-size: 14px;
  line-height: 1.5;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 60ch;
}

.et-toolbar .et-total {
  margin-left: auto;
}

.et-filter-svc {
  min-width: 180px;
}
.et-filter-sev {
  min-width: 160px;
}

.error-tracking-page .btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: var(--r-lg);
}

.data-table .col-date {
  width: 160px;
}
.data-table .col-svc {
  width: 130px;
}
.data-table .col-sev {
  width: 90px;
}
.data-table .col-status {
  width: 100px;
}
.data-table .col-actions {
  width: 140px;
}

.row-click {
  cursor: pointer;
}

.badge-muted {
  background: var(--c-surface-2);
  color: var(--c-txt-2);
}

.field-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.field-grow {
  flex: 1;
  min-width: 140px;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}
.github-check {
  width: auto;
  accent-color: var(--c-blue);
}
.github-check-label {
  margin-bottom: 0;
  cursor: pointer;
  font-size: 13px;
  color: var(--c-txt-2);
}

.modal-report {
  width: min(580px, calc(100vw - 32px));
}

/* Statistics cards grid */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.stat-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 16px 20px;
  min-width: 140px;
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--c-txt);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

.stat-warn { color: var(--c-warn); }
.stat-blue { color: var(--c-blue); }

.stat-label {
  font-size: 11px;
  color: var(--c-txt-2);
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Message cell truncation */
.msg-cell {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Expanded row details */
.expanded-row td {
  background: var(--c-surface-2) !important;
  padding: 16px !important;
}

.error-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.detail-label {
  font-size: 11px;
  color: var(--c-txt-3);
  min-width: 100px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-top: 2px;
}

.detail-item code {
  font-size: 12px;
  color: var(--c-txt);
  background: var(--c-surface);
  padding: 2px 6px;
  border-radius: var(--r-xs);
}

/* Traceback/extra display block */
.traceback-block {
  font-size: 11px;
  color: var(--c-txt-2);
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  padding: 10px 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', Courier, monospace;
}

/* Prevent textarea from resizing beyond modal boundaries */
.modal textarea {
  resize: vertical;
  max-height: 200px;
}
</style>
