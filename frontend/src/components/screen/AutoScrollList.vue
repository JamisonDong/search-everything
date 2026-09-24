<template>
  <div
    ref="viewport"
    class="auto-scroll"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
  >
    <div :style="{ transform: `translateY(-${offset}px)` }">
      <slot></slot>
      <!-- 复制一份实现首尾无缝循环滚动 -->
      <div v-if="overflowing" aria-hidden="true">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'

const props = defineProps({
  // 每秒滚动像素
  speed: { type: Number, default: 22 },
  // 数据变化时重新判断是否需要滚动
  watchKey: { type: [String, Number], default: 0 }
})

const viewport = ref(null)
const offset = ref(0)
const paused = ref(false)
const overflowing = ref(false)
let contentHeight = 0
let rafId = null
let last = 0

const measure = async () => {
  overflowing.value = false
  offset.value = 0
  await nextTick()
  const el = viewport.value
  if (!el) return
  contentHeight = el.firstElementChild.scrollHeight
  overflowing.value = contentHeight > el.clientHeight + 4
}

const tick = (now) => {
  const dt = last ? (now - last) / 1000 : 0
  last = now
  if (overflowing.value && !paused.value && contentHeight > 0) {
    offset.value = (offset.value + props.speed * dt) % contentHeight
  }
  rafId = requestAnimationFrame(tick)
}

onMounted(() => {
  measure()
  rafId = requestAnimationFrame(tick)
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
})

watch(() => props.watchKey, measure)
</script>

<style scoped>
.auto-scroll {
  height: 100%;
  overflow: hidden;
}
</style>
