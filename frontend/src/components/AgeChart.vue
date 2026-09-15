<template>
  <div class="h-full w-full flex flex-col">
    <div class="flex items-center justify-between pb-2">
      <div class="flex items-center gap-2">
        <div class="h-3 w-1 bg-indigo-400 rounded-full"></div>
        <span class="text-sm font-semibold text-slate-200">年龄结构与性别构成</span>
      </div>
      <div class="flex items-center gap-3 text-xs">
        <div class="flex items-center gap-1">
          <span class="h-2 w-2 rounded-full bg-blue-500"></span>
          <span class="text-slate-400">男性</span>
        </div>
        <div class="flex items-center gap-1">
          <span class="h-2 w-2 rounded-full bg-pink-500"></span>
          <span class="text-slate-400">女性</span>
        </div>
      </div>
    </div>
    <div ref="chartRef" class="flex-1 min-h-[260px] w-full"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data.length) return

  const categories = props.data.map(d => d.age_group)
  const males = props.data.map(d => d.male)
  const females = props.data.map(d => d.female)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(13, 21, 39, 0.95)',
      borderColor: '#6366f1',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    legend: { show: false },
    grid: {
      top: '15',
      right: '15',
      bottom: '25',
      left: '10',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        formatter: (v) => v >= 10000 ? `${(v / 10000).toFixed(1)}w` : v
      },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: [
      {
        name: '男性',
        type: 'bar',
        stack: 'total',
        data: males,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' },
            { offset: 1, color: '#1e40af' }
          ])
        }
      },
      {
        name: '女性',
        type: 'bar',
        stack: 'total',
        data: females,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ec4899' },
            { offset: 1, color: '#9d174d' }
          ])
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) chartInstance.dispose()
})

const handleResize = () => {
  if (chartInstance) chartInstance.resize()
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>
