<script setup>
defineProps({
  /** Встроенный блок на странице «Загруженные файлы» (/files) */
  embedded: { type: Boolean, default: false },
})

defineExpose({
  /** Совместимость с FilesPage; OAuth обрабатывается на странице файлов / модалке. */
  refreshOauthIntegrationStatus: () => {},
})
</script>

<template>
  <div class="sources-page" :class="{ embedded }">
    <div v-if="!embedded" class="page-toolbar">
      <h1 class="page-title">Загруженные файлы</h1>
    </div>

    <section class="section">
      <h2 class="section-title">Поддерживаемые источники</h2>
      <p class="section-lead">
        В интерфейсе доступны только способы, которые реально используются в вашем контуре.
      </p>

      <div class="source-cards">
        <div class="source-card">
          <span class="source-ico" aria-hidden="true">◧</span>
          <div class="source-body">
            <div class="source-name">Локальное хранилище</div>
            <div class="source-desc">
              Загрузка видео и аудио с компьютера — кнопка
              <strong>«Добавить файлы»</strong> на этой странице, затем постановка в очередь анализа.
            </div>
          </div>
        </div>
        <div class="source-card">
          <span class="source-ico" aria-hidden="true">◎</span>
          <div class="source-body">
            <div class="source-name">Яндекс.Диск</div>
            <div class="source-desc">
              Вход по OAuth и выбор файлов в
              <strong>«Добавить файлы»</strong> → вкладка Яндекс. Подключение — в разделе «Настройки».
            </div>
          </div>
        </div>
        <div class="source-card">
          <span class="source-ico" aria-hidden="true">◳</span>
          <div class="source-body">
            <div class="source-name">Google Диск</div>
            <div class="source-desc">
              Аналогично Яндексу: OAuth в «Настройках», импорт через
              <strong>«Добавить файлы»</strong> → Google.
            </div>
          </div>
        </div>
        <div class="source-card">
          <span class="source-ico" aria-hidden="true">☁</span>
          <div class="source-body">
            <div class="source-name">S3-совместимое хранилище</div>
            <div class="source-desc">
              Профили доступа (endpoint, ключи, bucket) в «Настройках»; обзор объектов и импорт — в
              <strong>«Добавить файлы»</strong> → S3.
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.sources-page {
  max-width: 900px;
}

.sources-page.embedded {
  max-width: none;
}

.page-toolbar {
  margin-bottom: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.section-lead {
  margin: 0 0 18px 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--c-txt-2);
}

.source-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.source-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 16px 18px;
  border-radius: var(--r-lg);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
}

.source-ico {
  font-size: 22px;
  line-height: 1;
  opacity: 0.85;
  flex-shrink: 0;
}

.source-body {
  min-width: 0;
}

.source-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--c-txt);
}

.source-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--c-txt-2);
}
</style>
