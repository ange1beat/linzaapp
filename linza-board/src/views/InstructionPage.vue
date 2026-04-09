<script setup>
import { NCard, NSpace, NTag, NIcon } from 'naive-ui'
import {
  CloudDownloadOutline,
  DocumentTextOutline,
  LinkOutline,
  ReaderOutline,
  VideocamOutline,
} from '@vicons/ionicons5'

const steps = [
  {
    num: 1,
    title: 'Подключение источника данных',
    icon: CloudDownloadOutline,
    desc: 'Настройте подключение к хранилищу данных: Google Drive, HTTP-сервер или S3-совместимое хранилище. Укажите параметры доступа и учётные данные в разделе «Источники данных».',
  },
  {
    num: 2,
    title: 'Ожидание отчёта в разделе «Результаты»',
    icon: DocumentTextOutline,
    desc: 'После анализа видео (очередь или пайплайн) отчёт появляется в «Результаты анализа»: файл, маркировка, число детекций и статус.',
  },
  {
    num: 3,
    title: 'Просмотр списка и маркировка',
    icon: ReaderOutline,
    desc: 'В таблице результатов задайте маркировку контента, при необходимости отметьте ревизию или передайте отчёт юристу.',
  },
  {
    num: 4,
    title: 'Плеер и PDF',
    icon: VideocamOutline,
    desc: 'Кнопка воспроизведения открывает встроенный плеер с детекциями на шкале времени. Если отчёт сформирован video-ai-filter, в шапке плеера доступно скачивание PDF.',
  },
  {
    num: 5,
    title: 'Переход из очереди',
    icon: LinkOutline,
    desc: 'Из «Очереди анализа» можно сразу открыть готовый отчёт на странице «Результаты» — плеер подставится автоматически.',
  },
]
</script>

<template>
  <div class="instruct">
    <div class="hdr">
      <h1 class="pg-t">Инструкция</h1>
      <p class="pg-d">Пошаговое руководство по использованию Linza Detector CGM</p>
    </div>

    <NSpace vertical :size="12">
      <NCard v-for="step in steps" :key="step.num" hoverable class="step-card">
        <NSpace :size="16" align="start">
          <div class="step-icon-wrap">
            <NIcon :component="step.icon" :size="24" color="var(--c-blue)" />
          </div>
          <div class="step-body">
            <NSpace align="center" :size="10" class="step-head">
              <NTag round type="primary" size="small">{{ step.num }}</NTag>
              <span class="step-title">{{ step.title }}</span>
            </NSpace>
            <p class="step-desc">{{ step.desc }}</p>
          </div>
        </NSpace>
      </NCard>
    </NSpace>
  </div>
</template>

<style scoped>
.instruct {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.hdr {
  margin-bottom: 24px;
}
.pg-t {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 8px;
  color: var(--c-txt);
}
.pg-d {
  font-size: 14px;
  line-height: 1.5;
  color: var(--c-txt-2);
  margin: 0;
  max-width: 60ch;
}

.step-card :deep(.n-card__content) {
  padding-top: 16px;
  padding-bottom: 16px;
}

.step-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--c-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--c-border);
}

.step-head {
  margin-bottom: 8px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-txt);
}

.step-desc {
  font-size: 13px;
  color: var(--c-txt-2);
  line-height: 1.6;
  margin: 0;
}
</style>
