/**
 * useErrorTracking composable — API layer for the Error Tracking page.
 *
 * Provides reactive state and methods for managing error records:
 * - fetchErrors()         — load error list from backend with filters
 * - fetchStats()          — load aggregate error statistics
 * - clearErrors()         — delete error records (all or by service)
 * - submitToGithub()      — mark error as submitted to GitHub Issues
 * - buildGitHubIssueUrl() — generate pre-filled GitHub new issue URL
 * - createManualError()   — manually create an error report from UI form
 *
 * All API calls use JWT token from useAuth for authentication.
 * Target GitHub repo for issues: BigDataQueen/Linza-debug
 */

import { ref } from 'vue'
import { useAuth } from './useAuth.js'

/** Reactive list of error records loaded from the backend */
const errors = ref([])

/** Total number of errors matching current filters */
const total = ref(0)

/** Aggregate statistics object: { total, last_hour, by_service, by_severity } */
const stats = ref({ total: 0, last_hour: 0, by_service: {}, by_severity: {} })

/** Loading state flag for UI spinners */
const loading = ref(false)

export function useErrorTracking() {
  const { getToken } = useAuth()

  /**
   * Build authorization headers for API requests.
   * Uses JWT token stored in localStorage via useAuth.
   * @returns {Object} headers object with Content-Type and Authorization
   */
  function headers() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`
    }
  }

  /**
   * Fetch error records from the backend API.
   *
   * Calls GET /api/errors/ with optional query parameters for filtering.
   * Updates the reactive `errors` and `total` refs.
   *
   * @param {Object} filters - optional filter parameters
   * @param {string} [filters.service]  - filter by service name
   * @param {string} [filters.severity] - filter by severity level
   * @param {number} [filters.limit=100]  - max records to return
   * @param {number} [filters.offset=0]   - pagination offset
   */
  async function fetchErrors(filters = {}) {
    loading.value = true
    try {
      // Build query string from non-empty filter values
      const params = new URLSearchParams()
      if (filters.service) params.set('service', filters.service)
      if (filters.severity) params.set('severity', filters.severity)
      if (filters.limit) params.set('limit', String(filters.limit))
      if (filters.offset) params.set('offset', String(filters.offset))

      const qs = params.toString()
      const url = `/api/errors/${qs ? '?' + qs : ''}`

      const res = await fetch(url, { headers: headers() })
      if (res.ok) {
        const data = await res.json()
        errors.value = data.errors
        total.value = data.total
      }
    } catch (e) {
      console.error('Failed to fetch errors:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch aggregate error statistics for dashboard cards.
   *
   * Calls GET /api/errors/stats and updates the reactive `stats` ref.
   * Returns: { total, last_hour, by_service, by_severity }
   */
  async function fetchStats() {
    try {
      const res = await fetch('/api/errors/stats', { headers: headers() })
      if (res.ok) {
        stats.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch error stats:', e)
    }
  }

  /**
   * Delete error records from the database.
   *
   * Calls DELETE /api/errors/ with optional service filter.
   * After deletion, reloads both errors list and stats.
   *
   * @param {string} [service] - if provided, only delete errors from this service
   */
  async function clearErrors(service) {
    try {
      const qs = service ? `?service=${encodeURIComponent(service)}` : ''
      const res = await fetch(`/api/errors/${qs}`, {
        method: 'DELETE',
        headers: headers()
      })
      if (res.ok) {
        await fetchErrors()
        await fetchStats()
      }
    } catch (e) {
      console.error('Failed to clear errors:', e)
    }
  }

  /**
   * Mark an error record as submitted to GitHub Issues.
   *
   * Calls POST /api/errors/{id}/submit-issue with the GitHub issue URL.
   * Updates the error status from 'new' to 'submitted' in the database.
   *
   * @param {number} errorId - ID of the error record
   * @param {string} issueUrl - full URL of the created GitHub Issue
   */
  async function submitToGithub(errorId, issueUrl) {
    try {
      const res = await fetch(`/api/errors/${errorId}/submit-issue`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ github_issue_url: issueUrl })
      })
      if (res.ok) {
        // Update local state to reflect the status change
        const idx = errors.value.findIndex(e => e.id === errorId)
        if (idx !== -1) {
          errors.value[idx].status = 'submitted'
          errors.value[idx].github_issue_url = issueUrl
        }
      }
    } catch (e) {
      console.error('Failed to submit error to GitHub:', e)
    }
  }

  /**
   * Manually create an error report from the UI form.
   *
   * Calls POST /api/errors/manual with the form data.
   * If submit_github is true, the backend returns a pre-filled GitHub
   * issue URL which the frontend opens in a new tab.
   *
   * After creation, reloads errors list and stats to reflect the new record.
   *
   * @param {Object} data - error report form data
   * @param {string} data.service     - source service name
   * @param {string} data.severity    - error severity level
   * @param {string} data.category    - error category
   * @param {string} data.message     - short error description (required)
   * @param {string} data.description - detailed description / steps to reproduce
   * @param {boolean} data.submit_github - whether to generate GitHub issue URL
   * @returns {Object} response with id, status, and optional github_issue_url
   */
  async function createManualError(data) {
    try {
      const res = await fetch('/api/errors/manual', {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(data)
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.detail || 'Ошибка создания отчёта')
      }
      const result = await res.json()

      // Reload data to show the new error in the table
      await fetchErrors()
      await fetchStats()

      return result
    } catch (e) {
      console.error('Failed to create manual error:', e)
      throw e
    }
  }

  /**
   * Build a pre-filled GitHub "New Issue" URL for a given error.
   *
   * Opens the GitHub issue creation form with title, body, and labels
   * pre-populated from the error record. The user creates the issue
   * manually in the browser, then we call submitToGithub() to record it.
   *
   * Target repo: BigDataQueen/Linza-debug
   *
   * @param {Object} error - error record object from the API
   * @returns {string} GitHub new issue URL with query parameters
   */
  function buildGitHubIssueUrl(error) {
    const repo = 'BigDataQueen/Linza-debug'
    const title = `[${error.service}] ${error.message}`.substring(0, 200)

    // Compose issue body with structured error details
    const bodyParts = [
      `## Error Report`,
      ``,
      `**Service:** \`${error.service}\``,
      `**Severity:** \`${error.severity}\``,
      error.category ? `**Category:** \`${error.category}\`` : null,
      error.endpoint ? `**Endpoint:** \`${error.method || 'GET'} ${error.endpoint}\`` : null,
      error.status_code ? `**Status Code:** ${error.status_code}` : null,
      error.request_id ? `**Request ID:** \`${error.request_id}\`` : null,
      `**Timestamp:** ${error.created_at}`,
      ``,
      `## Message`,
      `\`\`\``,
      error.message,
      `\`\`\``,
    ]

    // Add traceback section if available
    if (error.traceback) {
      bodyParts.push('', '## Traceback', '```python', error.traceback, '```')
    }

    // Add extra context if available
    if (error.extra) {
      bodyParts.push('', '## Extra Context', '```', error.extra, '```')
    }

    bodyParts.push('', '---', '*Reported from Linza Board error tracking interface.*')

    const body = bodyParts.filter(line => line !== null).join('\n')

    // Build URL with query parameters for pre-filling
    const params = new URLSearchParams({
      title,
      body,
      labels: ['bug', error.service].join(',')
    })

    return `https://github.com/${repo}/issues/new?${params.toString()}`
  }

  return {
    errors,
    total,
    stats,
    loading,
    fetchErrors,
    fetchStats,
    clearErrors,
    submitToGithub,
    createManualError,
    buildGitHubIssueUrl,
  }
}
