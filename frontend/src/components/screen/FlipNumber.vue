<template>
  <div class="flip-number">
    <template v-for="(ch, i) in chars" :key="i">
      <span v-if="ch === ','" class="sep">,</span>
      <span v-else class="digit">{{ ch }}</span>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  // 滚动动画时长 (毫秒)
  duration: { type: Number, default: 1600 }
})

const display = ref(0)
let rafId = null

const chars = computed(() => Math.round(display.value).toLocaleString('en-US').split(''))

const animateTo = (target) => {
  if (rafId) cancelAnimationFrame(rafId)
  const from = display.value
  const start = performance.now()
  const step = (now) => {
    const p = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - p, 3)
    display.value = from + (target - from) * eased
    if (p < 1) rafId = requestAnimationFrame(step)
  }
  rafId = requestAnimationFrame(step)
}

watch(() => props.value, (v) => animateTo(v || 0), { immediate: true })

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<style scoped>
.flip-number {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 8px;
}
.digit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 58px;
  height: 82px;
  font-family: 'Bahnschrift', 'DIN Alternate', 'DIN', 'Consolas', monospace;
  font-size: 60px;
  font-weight: 700;
  color: #ffd76a;
  text-shadow: 0 0 14px rgba(255, 196, 61, 0.6);
  background: linear-gradient(180deg, rgba(12, 52, 120, 0.95) 0%, rgba(6, 28, 70, 0.95) 50%, rgba(10, 44, 104, 0.95) 51%, rgba(5, 24, 60, 0.95) 100%);
  border: 1px solid rgba(64, 170, 255, 0.55);
  border-radius: 4px;
  box-shadow: inset 0 0 14px rgba(0, 140, 255, 0.35), 0 0 12px rgba(0, 100, 255, 0.25);
  font-variant-numeric: tabular-nums;
}
.sep {
  font-size: 48px;
  line-height: 1;
  color: #5fa8e6;
  padding-bottom: 6px;
}
</style>
