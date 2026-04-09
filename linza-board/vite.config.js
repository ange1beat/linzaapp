import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

/** Прямой заход на /files?... в dev — отдать index.html (Vue Router), иначе возможен 404. */
function spaFallback() {
  return {
    name: 'linza-spa-fallback',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        const raw = req.url || ''
        const path = raw.split('?')[0]
        if (
          req.method !== 'GET' ||
          path === '/' ||
          path.includes('.') ||
          path.startsWith('/@') ||
          path.startsWith('/api') ||
          path.startsWith('/node_modules') ||
          path.startsWith('/src') ||
          path.startsWith('/assets')
        ) {
          return next()
        }
        const q = raw.includes('?') ? raw.slice(raw.indexOf('?')) : ''
        req.url = '/index.html' + q
        next()
      })
    },
  }
}

export default defineConfig({
  plugins: [vue(), spaFallback()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('naive-ui')) return 'naive-ui'
          if (id.includes('motion-v') || id.includes('motion-dom')) return 'motion'
          if (id.includes('@vicons')) return 'vicons'
          if (id.includes('vue-router')) return 'vue-router'
          if (id.includes('/vue/') || id.endsWith('vue.js') || id.includes('@vue')) return 'vue-core'
        },
      },
    },
  },
  server: {
    proxy: {
      '/api/auth': 'http://localhost:8000',
      '/api/users': 'http://localhost:8000',
      '/api/settings': 'http://localhost:8000',
      '/api/reports': 'http://localhost:8000',
      '/api/errors': 'http://localhost:8000',
      '/api/analysis-queue': 'http://localhost:8000',
      '/api/portal': 'http://localhost:8000',
      '/api/detector-fetch': 'http://localhost:8000',
      '/api/integrations': 'http://localhost:8000',
      '/api/files': 'http://localhost:8001',
      '/api/config': 'http://localhost:8001',
      '/api/classifier': 'http://localhost:8002',
      '/api/vpleer': 'http://localhost:8003',
    },
  },
})
