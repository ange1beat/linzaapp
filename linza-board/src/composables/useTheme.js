import { ref, watch } from 'vue'

const STORAGE_KEY = 'linza_theme'

function readStored() {
  if (typeof localStorage === 'undefined') return 'dark'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) return stored === 'light' ? 'light' : 'dark'
  // No stored preference — detect OS preference (board#23)
  if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: light)').matches) {
    return 'light'
  }
  return 'dark'
}

const theme = ref(readStored())

function applyTheme(t) {
  document.documentElement.dataset.theme = t
  try {
    localStorage.setItem(STORAGE_KEY, t)
  } catch {
    /* ignore */
  }
}

applyTheme(theme.value)

watch(theme, (v) => applyTheme(v))

export function useTheme() {
  function setTheme(t) {
    theme.value = t === 'light' ? 'light' : 'dark'
  }
  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  return { theme, setTheme, toggleTheme }
}
