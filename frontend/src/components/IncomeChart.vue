<template>
  <div class="h-full w-full flex flex-col">
    <div class="flex items-center justify-between pb-2">
      <div class="flex items-center gap-2">
        <div class="h-3 w-1 bg-amber-400 rounded-full"></div>
        <span class="text-sm font-semibold text-slate-200">年收入梯度结构分布</span>
      </div>
      <span class="text-[11px] text-slate-400">单位: 人数</span>
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

  const categories = props.data.map(d => d.bracket)
  const counts = props.data.map(d => d.count)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(13, 21, 39, 0.95)',
      borderColor: '#f59e0b',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      formatter: (params) => {
        const item = params[0]
        return `
          <div class="font-bold text-amber-400">${item.name}</div>
          <div class="text-xs text-slate-300 mt-1">占比人数: <span class="font-mono text-white font-bold">${item.value.toLocaleString()}</span> 人</div>
        `
      }
    },
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
      axisLabel: { color: '#94a3b8', fontSize: 10, interval: 0 },
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
        name: '人数',
        type: 'bar',
        data: counts,
        barWidth: '45%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fbbf24' },
            { offset: 1, color: '#b45309' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          color: '#cbd5e1',
          fontSize: 9,
          formatter: (p) => p.value >= 10000 ? `${(p.value / 10000).toFixed(1)}w` : p.value
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
