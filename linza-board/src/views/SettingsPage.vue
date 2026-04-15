<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { useAuth } from '../composables/useAuth.js'
import { useStorage } from '../composables/useStorage.js'

const message = useMessage()
const { isSuperAdmin, currentUser } = useAuth()
const { profiles, loading, error, fetchProfiles, createProfile, updateProfile, deleteProfile, activateProfile, testConnection } = useStorage()

const showForm = ref(false)
const editingId = ref(null)
const testResult = ref(null)
const formError = ref('')

const form = ref({
  name: '',
  profile_type: 'source',
  s3_endpoint_url: '',
  s3_access_key_id: '',
  s3_secret_access_key: '',
  s3_bucket_name: '',
  s3_region: '',
  s3_tenant_id: '',
})

const sourceProfiles = computed(() => profiles.value.filter(p => p.profile_type === 'source'))
const destProfiles = computed(() => profiles.value.filter(p => p.profile_type === 'destination'))
const isAdmin = computed(() => currentUser.value?.role === 'admin')

function resetForm() {
  form.value = { name: '', profile_type: 'source', s3_endpoint_url: '', s3_access_key_id: '', s3_secret_access_key: '', s3_bucket_name: '', s3_region: '', s3_tenant_id: '' }
  editingId.value = null
  formError.value = ''
}

function openCreate(type) {
  resetForm()
  form.value.profile_type = type
  showForm.value = true
}

function openEdit(profile) {
  form.value = {
    name: profile.name,
    profile_type: profile.profile_type,
    s3_endpoint_url: profile.s3_endpoint_url,
    s3_access_key_id: '',
    s3_secret_access_key: '',
    s3_bucket_name: profile.s3_bucket_name,
    s3_region: profile.s3_region,
    s3_tenant_id: profile.s3_tenant_id,
  }
  editingId.value = profile.id
  showForm.value = true
  formError.value = ''
}

async function handleSubmit() {
  formError.value = ''
  try {
    const data = { ...form.value }
    if (!data.s3_access_key_id) delete data.s3_access_key_id
    if (!data.s3_secret_access_key) delete data.s3_secret_access_key

    if (editingId.value) {
      delete data.profile_type
      await updateProfile(editingId.value, data)
    } else {
      await createProfile(data)
    }
    showForm.value = false
    resetForm()
  } catch (e) {
    formError.value = e.message
  }
}

async function handleDelete(id) {
  if (!confirm('Удалить профиль?')) return
  try {
    await deleteProfile(id)
    message.success('Профиль удалён')
  } catch (e) {
    message.error(e.message || 'Не удалось удалить профиль')
  }
}

async function handleActivate(id) {
  try {
    await activateProfile(id)
    message.success('Профиль активирован')
  } catch (e) {
    message.error(e.message || 'Не удалось активировать')
  }
}

async function handleTest(id) {
  testResult.value = null
  try {
    const res = await testConnection(id)
    testResult.value = { id, status: 'ok', message: `Bucket: ${res.bucket}, Objects: ${res.objects}` }
  } catch (e) {
    testResult.value = { id, status: 'error', message: e.message }
  }
}

onMounted(fetchProfiles)
</script>

<template>
  <div class="settings">
    <div class="hdr">
      <div class="hdr-txt">
        <h1 class="pg-t">Настройки хранилищ</h1>
        <p class="pg-d">S3-профили: источники файлов и целевые бакеты для загрузки.</p>
      </div>
      <button type="button" class="btn btn-refresh" :disabled="loading" @click="fetchProfiles">
        {{ loading ? 'Загрузка…' : 'Обновить' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading" class="loading-banner">Загрузка профилей…</div>

    <!-- Source profiles -->
    <section class="section">
      <div class="section-header">
        <h2>Источники данных</h2>
        <p class="section-desc">Откуда загружать файлы для анализа</p>
        <button v-if="isSuperAdmin()" class="btn btn-primary" @click="openCreate('source')">+ Добавить</button>
      </div>
      <div v-if="sourceProfiles.length === 0" class="empty">Нет профилей</div>
      <div v-for="p in sourceProfiles" :key="p.id" class="profile-card" :class="{ active: p.is_active }">
        <div class="profile-header">
          <span class="profile-name">{{ p.name }}</span>
          <span v-if="p.is_active" class="badge badge-active">Активен</span>
        </div>
        <div class="profile-details">
          <div class="detail"><span class="label">Endpoint:</span> {{ p.s3_endpoint_url }}</div>
          <div class="detail"><span class="label">Bucket:</span> {{ p.s3_bucket_name }}</div>
          <div class="detail"><span class="label">Region:</span> {{ p.s3_region }}</div>
          <div class="detail"><span class="label">Key:</span> {{ p.s3_access_key_id }}</div>
          <div v-if="p.s3_tenant_id" class="detail"><span class="label">Tenant:</span> {{ p.s3_tenant_id }}</div>
        </div>
        <div v-if="testResult?.id === p.id" :class="['test-result', testResult.status]">
          {{ testResult.message }}
        </div>
        <div class="profile-actions">
          <button class="btn btn-sm" @click="handleTest(p.id)">Тест</button>
          <button class="btn btn-sm" @click="openEdit(p)">Изменить</button>
          <button v-if="isSuperAdmin() && !p.is_active" class="btn btn-sm btn-ok" @click="handleActivate(p.id)">Активировать</button>
          <button v-if="isSuperAdmin() && !p.is_active" class="btn btn-sm btn-danger" @click="handleDelete(p.id)">Удалить</button>
        </div>
      </div>
    </section>

    <!-- Destination profiles -->
    <section class="section">
      <div class="section-header">
        <h2>Хранилища для загрузки</h2>
        <p class="section-desc">Куда загружать файлы на обработку</p>
        <button v-if="isSuperAdmin()" class="btn btn-primary" @click="openCreate('destination')">+ Добавить</button>
      </div>
      <div v-if="destProfiles.length === 0" class="empty">Нет профилей</div>
      <div v-for="p in destProfiles" :key="p.id" class="profile-card" :class="{ active: p.is_active }">
        <div class="profile-header">
          <span class="profile-name">{{ p.name }}</span>
          <span v-if="p.is_active" class="badge badge-active">Активен</span>
        </div>
        <div class="profile-details">
          <div class="detail"><span class="label">Endpoint:</span> {{ p.s3_endpoint_url }}</div>
          <div class="detail"><span class="label">Bucket:</span> {{ p.s3_bucket_name }}</div>
          <div class="detail"><span class="label">Region:</span> {{ p.s3_region }}</div>
          <div class="detail"><span class="label">Key:</span> {{ p.s3_access_key_id }}</div>
          <div v-if="p.s3_tenant_id" class="detail"><span class="label">Tenant:</span> {{ p.s3_tenant_id }}</div>
        </div>
        <div v-if="testResult?.id === p.id" :class="['test-result', testResult.status]">
          {{ testResult.message }}
        </div>
        <div class="profile-actions">
          <button class="btn btn-sm" @click="handleTest(p.id)">Тест</button>
          <button v-if="isSuperAdmin()" class="btn btn-sm" @click="openEdit(p)">Изменить</button>
          <button v-if="isSuperAdmin() && !p.is_active" class="btn btn-sm btn-ok" @click="handleActivate(p.id)">Активировать</button>
          <button v-if="isSuperAdmin() && !p.is_active" class="btn btn-sm btn-danger" @click="handleDelete(p.id)">Удалить</button>
        </div>
      </div>
    </section>

    <!-- Create/Edit Modal -->
    <Transition name="linza-modal">
      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal">
        <h3>{{ editingId ? 'Редактирование профиля' : 'Новый профиль' }}</h3>
        <div v-if="formError" class="alert alert-error">{{ formError }}</div>
        <form @submit.prevent="handleSubmit">
          <div v-if="isSuperAdmin()" class="field">
            <label>Название</label>
            <input v-model="form.name" required placeholder="Production S3" />
          </div>
          <div class="field">
            <label>S3 Endpoint URL</label>
            <input v-model="form.s3_endpoint_url" placeholder="https://s3.cloud.ru" />
          </div>
          <div class="field">
            <label>Access Key ID</label>
            <input v-model="form.s3_access_key_id" placeholder="Оставьте пустым, чтобы не менять" />
          </div>
          <div class="field">
            <label>Secret Access Key</label>
            <input v-model="form.s3_secret_access_key" type="password" placeholder="Оставьте пустым, чтобы не менять" />
          </div>
          <div v-if="isSuperAdmin()" class="field">
            <label>Bucket Name</label>
            <input v-model="form.s3_bucket_name" placeholder="linzadata" />
          </div>
          <div v-if="isSuperAdmin()" class="field">
            <label>Region</label>
            <input v-model="form.s3_region" placeholder="ru-central-1" />
          </div>
          <div v-if="isSuperAdmin()" class="field">
            <label>Tenant ID</label>
            <input v-model="form.s3_tenant_id" placeholder="Для мультитенантных S3 (опционально)" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn" @click="showForm = false">Отмена</button>
            <button type="submit" class="btn btn-primary">{{ editingId ? 'Сохранить' : 'Создать' }}</button>
          </div>
        </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.settings {
  max-width: 880px;
  width: 100%;
  margin: 0 auto;
}

.hdr {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.hdr-txt {
  min-width: 0;
  flex: 1;
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
  max-width: 52ch;
}
.btn-refresh {
  flex-shrink: 0;
}

.section { margin-bottom: 32px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.section-header h2 { font-size: 14px; font-weight: 600; }
.section-desc { font-size: 12px; color: var(--c-txt-2); flex: 1; }

.profile-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 14px;
  margin-bottom: 8px;
}
.profile-card.active { border-color: rgba(10,111,255,0.4); }
.profile-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.profile-name { font-weight: 600; font-size: 13px; }
.badge-active { font-size: 10px; padding: 2px 6px; border-radius: var(--r-xs); background: var(--c-ok-bg); color: var(--c-ok); }
.profile-details { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 12px; color: var(--c-txt-2); }
.detail .label { color: var(--c-txt-3); }
.profile-actions { display: flex; gap: 6px; margin-top: 10px; }

.test-result { font-size: 12px; margin-top: 8px; padding: 6px 10px; border-radius: var(--r-sm); }
.test-result.ok { background: var(--c-ok-bg); color: var(--c-ok); }
.test-result.error { background: var(--c-err-bg); color: var(--c-err); }

.empty { font-size: 12px; color: var(--c-txt-3); padding: 12px; }

.btn { padding: 5px 12px; border-radius: var(--r-sm); font-size: 12px; border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-txt); cursor: pointer; font-family: inherit; }
.btn:hover { background: var(--c-surface-2); }
.btn-sm { padding: 3px 8px; font-size: 11px; }
.btn-primary { background: var(--c-blue); color: #fff; border-color: var(--c-blue); }
.btn-primary:hover { background: var(--c-blue-hover); }
.btn-ok { border-color: rgba(52,211,153,0.4); color: var(--c-ok); }
.btn-danger { border-color: rgba(220,38,38,0.4); color: var(--c-err); }
.btn-danger:hover { background: var(--c-err-bg); }

.modal-overlay { position: fixed; inset: 0; background: var(--c-modal-overlay); display: flex; align-items: center; justify-content: center; z-index: 5000; }
.modal { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-xl); padding: 24px; width: 460px; max-height: 90vh; overflow-y: auto; }
.modal h3 { font-size: 15px; margin-bottom: 16px; }
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 12px; color: var(--c-txt-2); margin-bottom: 4px; }
.field input { width: 100%; padding: 7px 10px; border-radius: var(--r-sm); border: 1px solid var(--c-border); background: var(--c-surface-2); color: var(--c-txt); font-size: 13px; font-family: inherit; }
.field input:focus { outline: none; border-color: var(--c-blue); }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }

.alert-error { background: var(--c-err-bg); color: var(--c-err); padding: 8px 12px; border-radius: var(--r-md); font-size: 12px; margin-bottom: 12px; }
.loading-banner { font-size: 12px; color: var(--c-txt-3); margin-bottom: 12px; }
</style>
