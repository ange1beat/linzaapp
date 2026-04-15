<script setup>
/**
 * Полоска загрузки при смене маршрута (ожидание ленивых чанков).
 * Рендерить только внутри NLoadingBarProvider.
 */
import { onBeforeUnmount } from 'vue'
import { useRouter, isNavigationFailure } from 'vue-router'
import { useLoadingBar } from 'naive-ui'

const router = useRouter()
const bar = useLoadingBar()

let pending = 0

const removeBefore = router.beforeEach((to, from, next) => {
  if (to.fullPath !== from.fullPath) {
    if (pending === 0) bar.start()
    pending++
  }
  next()
})

const removeAfter = router.afterEach((_to, _from, failure) => {
  if (pending === 0) return
  pending = Math.max(0, pending - 1)
  if (pending === 0) {
    if (failure && isNavigationFailure(failure)) bar.error()
    else bar.finish()
  }
})

const removeErr = router.onError(() => {
  if (pending > 0) {
    pending = 0
    bar.error()
  }
})

onBeforeUnmount(() => {
  removeBefore()
  removeAfter()
  removeErr()
})
</script>

<template>
  <span aria-hidden="true" class="route-progress-root" />
</template>

<style scoped>
.route-progress-root {
  display: none;
}
</style>
