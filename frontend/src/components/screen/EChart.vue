<template>
  <div ref="chartRef" class="h-full w-full"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['chart-click'])

const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(props.option)
  chartInstance.on('click', (params) => emit('chart-click', params))

  // 大屏整体缩放或容器尺寸变化时自适应重绘
  resizeObserver = new ResizeObserver(() => chartInstance && chartInstance.resize())
  resizeObserver.observe(chartRef.value)
})

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
  if (chartInstance) chartInstance.dispose()
})

watch(() => props.option, (opt) => {
  if (chartInstance) chartInstance.setOption(opt, true)
})
</script>
