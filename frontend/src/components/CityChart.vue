<template>
  <div class="h-full w-full flex flex-col">
    <div class="flex items-center justify-between pb-2">
      <div class="flex items-center gap-2">
        <div class="h-3 w-1 bg-cyan-400 rounded-full"></div>
        <span class="text-sm font-semibold text-slate-200">重点城市人口分布 (Top 12)</span>
      </div>
      <span class="text-[11px] text-slate-400">点击城市可直接下钻筛选</span>
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

const emit = defineEmits(['select-city'])

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)

  chartInstance.on('click', (params) => {
    if (params.name) {
      emit('select-city', params.name)
    }
  })

  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data.length) return

  // 反转使得最多的人口排在上方
  const reversed = [...props.data].reverse()
  const cities = reversed.map(d => d.city)
  const counts = reversed.map(d => d.count)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(13, 21, 39, 0.95)',
      borderColor: '#00f0ff',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      formatter: (params) => {
        const item = reversed[params[0].dataIndex]
        return `
          <div class="font-bold text-cyan-400">${item.city}</div>
          <div class="text-xs text-slate-300 mt-1">人员总数: <span class="font-mono text-white font-bold">${item.count.toLocaleString()}</span> 人</div>
          <div class="text-xs text-slate-300">人均年收入: <span class="font-mono text-amber-400 font-bold">¥${item.avg_income.toLocaleString()}</span></div>
          <div class="text-[10px] text-cyan-300 mt-1">💡 点击联动下方表格</div>
        `
      }
    },
    grid: {
      top: '10',
      right: '25',
      bottom: '10',
      left: '10',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748b',
        fontSize: 10,
        formatter: (v) => v >= 10000 ? `${(v / 10000).toFixed(1)}w` : v
      },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: cities,
      axisLabel: { color: '#cbd5e1', fontSize: 11 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    series: [
      {
        name: '人员数',
        type: 'bar',
        data: counts,
        barWidth: '55%',
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: 'rgba(22, 119, 255, 0.6)' },
            { offset: 1, color: '#00f0ff' }
          ])
        },
        label: {
          show: true,
          position: 'right',
          color: '#94a3b8',
          fontSize: 10,
          formatter: (p) => p.value.toLocaleString()
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
