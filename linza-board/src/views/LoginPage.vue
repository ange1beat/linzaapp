<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NInput,
  NButton,
  NIcon,
  NAlert,
} from 'naive-ui'
import { SunnyOutline, MoonOutline, EyeOutline, EyeOffOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth.js'
import { useTheme } from '../composables/useTheme.js'
import { landingPathForPortalRole } from '../utils/portalLanding.js'

const router = useRouter()
const { login, authError, activePortalRole } = useAuth()
const { theme, toggleTheme } = useTheme()

const loginInput = ref('')
const passwordInput = ref('')
const loading = ref(false)
const showPassword = ref(false)

async function handleSubmit() {
  if (loading.value) return
  loading.value = true
  const ok = await login(loginInput.value, passwordInput.value)
  loading.value = false
  if (ok) router.push(landingPathForPortalRole(activePortalRole() || 'operator'))
}
</script>

<template>
  <div class="login-root">
    <div class="login-bg" aria-hidden="true" />

    <NButton
      quaternary
      circle
      class="login-theme-toggle"
      aria-label="Переключить тему"
      @click="toggleTheme"
    >
      <template #icon>
        <NIcon :component="theme === 'dark' ? SunnyOutline : MoonOutline" :size="20" />
      </template>
    </NButton>

    <div class="login-wrapper">
      <NCard class="login-card" :bordered="false" content-style="padding: clamp(24px, 5vw, 36px);">
        <div class="login-brand">
          <img
            src="../assets/linza-detector-logo.svg"
            alt="Linza Detector"
            class="login-logo"
            width="240"
            height="58"
            decoding="async"
          />
          <p class="login-tagline">Портал проверки контента</p>
        </div>

        <h1 class="login-title">Вход в систему</h1>

        <form class="login-form" @submit.prevent="handleSubmit" novalidate>
          <label class="sr-only" for="login-user">Логин</label>
          <NInput
            id="login-user"
            v-model:value="loginInput"
            placeholder="Логин или email"
            size="large"
            :input-props="{ autocomplete: 'username' }"
          />

          <label class="sr-only" for="login-pass">Пароль</label>
          <NInput
            id="login-pass"
            v-model:value="passwordInput"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Пароль"
            size="large"
            :input-props="{ autocomplete: 'current-password' }"
          >
            <template #suffix>
              <NButton
                text
                tabindex="-1"
                :aria-pressed="showPassword"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showPassword = !showPassword"
              >
                <template #icon>
                  <NIcon :component="showPassword ? EyeOffOutline : EyeOutline" />
                </template>
              </NButton>
            </template>
          </NInput>

          <NAlert v-if="authError" type="error" :bordered="false" class="login-alert">
            {{ authError }}
          </NAlert>

          <NButton
            type="primary"
            size="large"
            block
            attr-type="submit"
            :loading="loading"
            :disabled="loading"
          >
            Войти
          </NButton>
        </form>

        <NButton text type="primary" class="forgot-link">
          Забыл пароль?
        </NButton>
      </NCard>
    </div>

    <footer class="login-foot">
      Linza Detector · {{ new Date().getFullYear() }}
    </footer>
  </div>
</template>

<style scoped>
.login-root {
  position: relative;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: max(24px, env(safe-area-inset-top)) max(20px, env(safe-area-inset-right)) max(24px, env(safe-area-inset-bottom)) max(20px, env(safe-area-inset-left));
  background: var(--c-bg);
}

.login-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, var(--c-blue-dim), transparent 55%),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(45, 212, 191, 0.06), transparent 45%),
    radial-gradient(circle at 0% 80%, rgba(148, 163, 184, 0.08), transparent 40%);
  opacity: 1;
}

.login-theme-toggle {
  position: fixed;
  top: max(16px, env(safe-area-inset-top));
  right: max(16px, env(safe-area-inset-right));
  z-index: 20;
}

.login-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  animation: login-rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.login-card {
  border-radius: var(--r-xl) !important;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--c-border) !important;
  background: color-mix(in srgb, var(--c-surface) 94%, transparent);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.login-brand {
  text-align: center;
  margin-bottom: 20px;
}

.login-logo {
  width: min(240px, 78vw);
  height: auto;
  display: block;
  margin: 0 auto 10px;
  object-fit: contain;
}

.login-tagline {
  margin: 0;
  font-size: 13px;
  color: var(--c-txt-2);
  line-height: 1.4;
}

.login-title {
  margin: 0 0 24px;
  font-size: clamp(18px, 4vw, 21px);
  font-weight: 700;
  line-height: 1.25;
  text-align: center;
  letter-spacing: -0.02em;
  color: var(--c-txt);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-alert {
  border-radius: var(--r-sm) !important;
}

.forgot-link {
  display: block;
  width: 100%;
  margin-top: 18px;
  text-align: center;
  opacity: 0.85;
}

.login-foot {
  position: relative;
  z-index: 1;
  margin-top: 24px;
  font-size: 12px;
  color: var(--c-txt-3);
  animation: login-fade 0.55s ease 0.08s both;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes login-rise {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes login-fade {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-wrapper,
  .login-foot {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
</style>
