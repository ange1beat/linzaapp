<template>
  <div class="about">
    <div class="hdr">
      <h1 class="pg-t">О системе</h1>
      <p class="pg-d">Краткое описание платформы Linza Detector CGM</p>
    </div>

    <NCard class="ver-card">
      <NSpace align="baseline" :size="12">
        <span class="product-name">Linza Detector</span>
        <NTag type="info" round>v1.0</NTag>
      </NSpace>
    </NCard>

    <NCard title="Описание" class="desc-card">
      <p class="desc-text">
        Linza Detector CGM — система автоматического анализа видеоданных для обнаружения и классификации объектов.
        Платформа обеспечивает загрузку видеофайлов из различных хранилищ, обработку с помощью нейросетевых моделей
        детекции, и визуализацию результатов через веб-интерфейс и встроенный видеоплеер.
      </p>
    </NCard>
  </div>
</template>

<script setup>
import { NCard, NTag, NSpace } from 'naive-ui'
</script>

<style scoped>
.about {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.hdr {
  margin-bottom: 20px;
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
}

.ver-card {
  margin-bottom: 20px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-txt);
}

.desc-card :deep(.n-card-header) {
  padding-bottom: 8px;
}

.desc-text {
  font-size: 13px;
  color: var(--c-txt-2);
  line-height: 1.7;
  margin: 0;
}
</style>
