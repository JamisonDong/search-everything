<template>
  <div 
    v-show="visible" 
    ref="watermarkContainer"
    class="fixed inset-0 z-[9999] pointer-events-none overflow-hidden select-none"
    aria-hidden="true"
  >
    <canvas ref="canvasRef" class="w-full h-full opacity-35"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: true
  },
  operator: {
    type: String,
    default: '操作员-01'
  },
  terminalId: {
    type: String,
    default: 'SEC-PC-01'
  }
})

const watermarkContainer = ref(null)
const canvasRef = ref(null)
let timer = null
let observer = null

const renderWatermark = () => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const width = window.innerWidth
  const height = window.innerHeight

  canvas.width = width
  canvas.height = height

  ctx.clearRect(0, 0, width, height)

  const now = new Date()
  const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`
  const text1 = `【内部数据 · 严禁外传】`
  const text2 = `${props.operator} | ${props.terminalId} | ${timeStr}`

  ctx.font = '14px sans-serif'
  ctx.fillStyle = 'rgba(120, 180, 255, 0.22)'
  ctx.rotate((-22 * Math.PI) / 180)

  const stepX = 360
  const stepY = 180

  for (let x = -width; x < width * 2; x += stepX) {
    for (let y = -height; y < height * 2; y += stepY) {
      ctx.fillText(text1, x, y)
      ctx.fillText(text2, x, y + 22)
    }
  }

  ctx.rotate((22 * Math.PI) / 180) // 恢复
}

onMounted(() => {
  renderWatermark()
  window.addEventListener('resize', renderWatermark)
  
  // 每秒更新时间戳水印
  timer = setInterval(renderWatermark, 1000)

  // 防篡改 DOM 观察者
  if (watermarkContainer.value && window.MutationObserver) {
    observer = new MutationObserver(() => {
      if (watermarkContainer.value) {
        watermarkContainer.value.style.display = props.visible ? 'block' : 'none'
        watermarkContainer.value.style.pointerEvents = 'none'
      }
    })
    observer.observe(watermarkContainer.value, { attributes: true, childList: true, subtree: true })
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (observer) observer.disconnect()
  window.removeEventListener('resize', renderWatermark)
})

watch(() => [props.visible, props.operator], () => {
  renderWatermark()
})
</script>
