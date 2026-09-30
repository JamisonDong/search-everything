<template>
  <div class="screen-stage">
    <!-- 固定 1920×1080 设计稿，按窗口等比缩放，任何分辨率下均完整铺满一屏 -->
    <div class="screen-canvas" :style="canvasStyle">
      <!-- ============ 顶部标题栏 ============ -->
      <header class="screen-header">
        <svg class="header-bg" viewBox="0 0 1920 100" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="hdrLine" x1="0" x2="1">
              <stop offset="0" stop-color="#33d6ff" stop-opacity="0" />
              <stop offset="0.3" stop-color="#33d6ff" stop-opacity="0.9" />
              <stop offset="0.7" stop-color="#33d6ff" stop-opacity="0.9" />
              <stop offset="1" stop-color="#33d6ff" stop-opacity="0" />
            </linearGradient>
            <linearGradient id="hdrFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="#0b3a86" stop-opacity="0.85" />
              <stop offset="1" stop-color="#06224f" stop-opacity="0.2" />
            </linearGradient>
          </defs>
          <path d="M560 0 H1360 L1304 80 H616 Z" fill="url(#hdrFill)" />
          <path d="M0 58 H530 L590 90 H1330 L1390 58 H1920" fill="none" stroke="url(#hdrLine)" stroke-width="2" />
          <path d="M616 80 H1304" stroke="#33d6ff" stroke-width="3" stroke-opacity="0.9" />
          <path d="M880 96 H1040" stroke="#ffc53d" stroke-width="3" />
        </svg>

        <div class="header-side header-left">
          <span class="clock-time">{{ clock.time }}</span>
          <span class="clock-date">{{ clock.date }}<br />{{ clock.week }}</span>
        </div>

        <div class="header-title">
          <h1>人员数据态势分析大屏</h1>
          <p>PERSONNEL DATA SITUATION AWARENESS PLATFORM</p>
        </div>

        <div class="header-side header-right">
          <span class="sec-badge">内部数据 · 严禁外传</span>
          <button class="hdr-btn" @click="emit('open-search')">检索工作台</button>
          <button class="hdr-btn" @click="emit('open-audit')">安全审计</button>
          <button class="hdr-btn" @click="toggleFullscreen">{{ isFullscreen ? '退出全屏' : '全屏展示' }}</button>
        </div>
      </header>

      <!-- ============ 主体三栏 ============ -->
      <main class="screen-body">
        <!-- 左栏 -->
        <div class="col">
          <ScreenPanel title="核心指标概览" class="h-[330px]">
            <div class="kpi-grid">
              <div v-for="item in kpiTiles" :key="item.label" class="kpi-tile">
                <div class="kpi-label">{{ item.label }}</div>
                <div class="kpi-value" :style="{ color: item.color }">
                  {{ item.value }}<small>{{ item.unit }}</small>
                </div>
              </div>
            </div>
          </ScreenPanel>

          <ScreenPanel title="年龄结构金字塔" class="flex-1">
            <template #extra>
              <span class="legend"><i style="background:#3d8bff"></i>男性<i style="background:#ff5fa2"></i>女性</span>
            </template>
            <EChart :option="agePyramidOption" />
          </ScreenPanel>
        </div>

        <!-- 中栏 -->
        <div class="col">
          <div class="hero">
            <div class="hero-label">人员数据库收录总量<span>（人）</span></div>
            <FlipNumber :value="kpi.total_count" />
            <div class="hero-stats">
              <div><span>覆盖城市</span><b>{{ kpi.total_cities }}</b><em>个</em></div>
              <div><span>数据容量</span><b>{{ formatSize(systemStatus.database_size_mb) }}</b></div>
              <div><span>聚合耗时</span><b>{{ Math.round(executionMs) }}</b><em>ms</em></div>
              <div><span>更新日期</span><b class="text-[20px]">{{ lastImported }}</b></div>
            </div>
          </div>

          <ScreenPanel title="重点城市人员分布与人均收入" extra="点击城市可下钻检索" class="flex-1">
            <EChart :option="cityOption" @chart-click="onCityClick" />
          </ScreenPanel>

          <div class="flex gap-4 h-[290px]">
            <ScreenPanel title="性别构成" class="flex-1">
              <EChart :option="genderOption" />
            </ScreenPanel>
            <ScreenPanel title="年收入梯度结构" class="flex-1">
              <EChart :option="incomeOption" />
            </ScreenPanel>
          </div>
        </div>

        <!-- 右栏 -->
        <div class="col">
          <ScreenPanel title="城市人员规模排行" class="flex-1">
            <div class="rank-head">
              <span>排名</span><span>城市</span><span class="text-right">人数</span><span class="text-right">占比</span>
            </div>
            <div class="rank-scroll">
              <AutoScrollList class="fade-edges" :watch-key="cityData.length">
                <div
                  v-for="(c, i) in cityData"
                  :key="c.city"
                  class="rank-row"
                  @click="emit('drill-city', c.city)"
                >
                  <span class="rank-no" :class="'rank-' + Math.min(i + 1, 4)">{{ i + 1 }}</span>
                  <div class="rank-city">
                    <div>{{ c.city }}</div>
                    <div class="rank-bar"><i :style="{ width: (c.count / maxCityCount * 100) + '%' }"></i></div>
                  </div>
                  <span class="rank-count">{{ c.count.toLocaleString() }}</span>
                  <span class="rank-share">{{ share(c.count) }}%</span>
                </div>
              </AutoScrollList>
            </div>
          </ScreenPanel>

          <ScreenPanel title="安全审计实时动态" extra="全部操作留痕" class="h-[360px]">
            <AutoScrollList class="fade-edges" :watch-key="auditLogs.length" :speed="18">
              <div v-for="(log, i) in auditLogs" :key="i" class="audit-row">
                <span class="audit-time">{{ formatLogTime(log.timestamp) }}</span>
                <span class="audit-tag" :class="log.action === 'SEARCH' ? 'tag-search' : 'tag-view'">
                  {{ actionLabel(log.action) }}
                </span>
                <span class="audit-text">{{ log.operator }} · {{ describeLog(log) }}</span>
              </div>
              <div v-if="!auditLogs.length" class="audit-empty">暂无操作记录</div>
            </AutoScrollList>
          </ScreenPanel>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import EChart from '../components/screen/EChart.vue'
import FlipNumber from '../components/screen/FlipNumber.vue'
import AutoScrollList from '../components/screen/AutoScrollList.vue'

const emit = defineEmits(['open-search', 'open-audit', 'drill-city', 'cities-loaded'])

const DESIGN_W = 1920
const DESIGN_H = 1080

// ---------------- 数据状态 ----------------
const kpi = ref({ total_count: 0, total_cities: 0, avg_age: 0, avg_income: 0, median_income: 0, male_count: 0, female_count: 0, male_ratio: 0, female_ratio: 0 })
const cityData = ref([])
const ageData = ref([])
const incomeData = ref([])
const executionMs = ref(0)
const systemStatus = ref({})
const auditLogs = ref([])

// ---------------- 等比缩放 ----------------
const scale = ref(1)
const fitScreen = () => {
  scale.value = Math.min(window.innerWidth / DESIGN_W, window.innerHeight / DESIGN_H)
}
const canvasStyle = computed(() => ({
  width: `${DESIGN_W}px`,
  height: `${DESIGN_H}px`,
  transform: `translate(-50%, -50%) scale(${scale.value})`
}))

// ---------------- 时钟 ----------------
const WEEK = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
const pad = (n) => String(n).padStart(2, '0')
const clock = ref({ time: '', date: '', week: '' })
const updateClock = () => {
  const d = new Date()
  clock.value = {
    time: `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`,
    date: `${d.getFullYear()}年${pad(d.getMonth() + 1)}月${pad(d.getDate())}日`,
    week: WEEK[d.getDay()]
  }
}

// ---------------- 全屏 ----------------
const isFullscreen = ref(false)
const toggleFullscreen = () => {
  if (document.fullscreenElement) document.exitFullscreen()
  else document.documentElement.requestFullscreen?.()
}
const onFullscreenChange = () => { isFullscreen.value = !!document.fullscreenElement }

// ---------------- 数据加载 ----------------
const fetchStats = async () => {
  try {
    const data = await (await fetch('/api/dashboard/stats')).json()
    kpi.value = data.kpi
    cityData.value = data.city_distribution || []
    ageData.value = data.age_pyramid || []
    incomeData.value = data.income_distribution || []
    executionMs.value = data.total_execution_ms || 0
    if (cityData.value.length) emit('cities-loaded', cityData.value.map(c => c.city))
  } catch (e) {
    console.error('Failed to fetch dashboard stats:', e)
  }
}

const fetchSystemStatus = async () => {
  try {
    systemStatus.value = await (await fetch('/api/system/status')).json()
  } catch (e) {
    console.error('Failed to fetch system status:', e)
  }
}

const fetchAudit = async () => {
  try {
    auditLogs.value = await (await fetch('/api/audit/logs?limit=30')).json()
  } catch (e) {
    console.error('Failed to fetch audit logs:', e)
  }
}

// ---------------- 派生指标 ----------------
const toWan = (v) => (v >= 10000 ? `${(v / 10000).toFixed(v >= 1e6 ? 0 : 1)}万` : `${v}`)
const yuan = (v) => Math.round(v || 0).toLocaleString()

const highIncomeCount = computed(() =>
  incomeData.value.filter(d => d.bracket === '50-100万' || d.bracket === '100万以上').reduce((s, d) => s + d.count, 0)
)

const kpiTiles = computed(() => [
  { label: '人均年收入', value: yuan(kpi.value.avg_income), unit: '元', color: '#ffd76a' },
  { label: '年收入中位数', value: yuan(kpi.value.median_income), unit: '元', color: '#ffd76a' },
  { label: '平均年龄', value: kpi.value.avg_age || 0, unit: '岁', color: '#5ce1ff' },
  {
    label: '性别比 (女=100)',
    value: kpi.value.female_count ? (kpi.value.male_count / kpi.value.female_count * 100).toFixed(1) : '-',
    unit: '',
    color: '#5ce1ff'
  },
  { label: '覆盖城市', value: kpi.value.total_cities || 0, unit: '个', color: '#36e2a0' },
  { label: '年收入50万以上', value: highIncomeCount.value.toLocaleString(), unit: '人', color: '#36e2a0' }
])

const lastImported = computed(() => {
  const v = systemStatus.value.last_imported_at
  return v && /^\d{4}-\d{2}-\d{2}/.test(v) ? v.slice(0, 10) : '—'
})

const maxCityCount = computed(() => Math.max(1, ...cityData.value.map(c => c.count)))
const share = (count) => (kpi.value.total_count ? (count / kpi.value.total_count * 100).toFixed(1) : '0.0')

const formatSize = (mb) => {
  if (!mb) return '—'
  return mb >= 1024 ? `${(mb / 1024).toFixed(2)} GB` : `${mb.toFixed(0)} MB`
}

// 审计动态只展示行为摘要，不在大屏上暴露检索关键词等个人信息
const actionLabel = (a) => ({ SEARCH: '检索', VIEW_DETAIL: '调阅', EXPORT_ATTEMPT: '导出' }[a] || a)
const maskId = (id) => (id && id.length >= 10 ? `${id.slice(0, 6)}********${id.slice(-4)}` : '********')
const describeLog = (log) => {
  const d = log.details || {}
  if (log.action === 'SEARCH') {
    const scope = d.city ? `${d.city}范围` : '全库范围'
    return `${scope}检索，命中 ${(d.total_hits ?? 0).toLocaleString()} 条`
  }
  if (log.action === 'VIEW_DETAIL') return `调阅档案 ${maskId(d.person_id)}`
  return '执行敏感操作'
}
const formatLogTime = (ts) => (ts ? ts.slice(11, 19) : '')

// ---------------- 图表配置 ----------------
const AXIS_LABEL = { color: '#9cc3e6', fontSize: 14 }
const SPLIT_LINE = { lineStyle: { color: 'rgba(80, 150, 230, 0.15)', type: 'dashed' } }
const TOOLTIP = {
  backgroundColor: 'rgba(6, 30, 70, 0.95)',
  borderColor: '#33d6ff',
  textStyle: { color: '#e8f4ff', fontSize: 14 }
}
const vGrad = (top, bottom) => new echarts.graphic.LinearGradient(0, 0, 0, 1, [
  { offset: 0, color: top }, { offset: 1, color: bottom }
])
const hGrad = (left, right) => new echarts.graphic.LinearGradient(0, 0, 1, 0, [
  { offset: 0, color: left }, { offset: 1, color: right }
])

const agePyramidOption = computed(() => {
  const groups = ageData.value.map(d => d.age_group)
  const peak = Math.max(1, ...ageData.value.flatMap(d => [d.male, d.female]))
  const bound = peak * 1.35
  return {
    tooltip: {
      ...TOOLTIP,
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (ps) => `${ps[0].name}<br/>` + ps.map(p => `${p.marker}${p.seriesName}：${Math.abs(p.value).toLocaleString()} 人`).join('<br/>')
    },
    grid: { top: 10, bottom: 30, left: 10, right: 10, containLabel: true },
    xAxis: {
      type: 'value',
      min: -bound,
      max: bound,
      axisLabel: { ...AXIS_LABEL, showMinLabel: false, showMaxLabel: false, formatter: (v) => toWan(Math.abs(Math.round(v))) },
      splitLine: SPLIT_LINE
    },
    yAxis: {
      type: 'category',
      data: groups,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(80, 150, 230, 0.4)' } },
      axisLabel: { ...AXIS_LABEL, fontSize: 15, color: '#d6ebff' }
    },
    series: [
      {
        name: '男性',
        type: 'bar',
        stack: 'age',
        barWidth: 22,
        data: ageData.value.map(d => -d.male),
        itemStyle: { color: hGrad('#3d8bff', '#1a4fb5'), borderRadius: [4, 0, 0, 4] },
        label: { show: true, position: 'left', color: '#9cc3e6', fontSize: 13, formatter: (p) => toWan(Math.abs(p.value)) }
      },
      {
        name: '女性',
        type: 'bar',
        stack: 'age',
        data: ageData.value.map(d => d.female),
        itemStyle: { color: hGrad('#b3337a', '#ff5fa2'), borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: 'right', color: '#9cc3e6', fontSize: 13, formatter: (p) => toWan(p.value) }
      }
    ]
  }
})

const cityOption = computed(() => ({
  tooltip: {
    ...TOOLTIP,
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (ps) => `${ps[0].name}<br/>` + ps.map(p =>
      `${p.marker}${p.seriesName}：${p.seriesIndex === 0 ? `${p.value.toLocaleString()} 人` : `¥ ${Math.round(p.value).toLocaleString()}`}`
    ).join('<br/>')
  },
  legend: {
    top: 0,
    right: 10,
    textStyle: { color: '#b8d6f2', fontSize: 14 },
    itemWidth: 16,
    itemHeight: 10,
    data: ['人员数量', '人均年收入']
  },
  grid: { top: 44, bottom: 10, left: 10, right: 10, containLabel: true },
  xAxis: {
    type: 'category',
    data: cityData.value.map(c => c.city.replace(/市$/, '')),
    axisTick: { show: false },
    axisLine: { lineStyle: { color: 'rgba(80, 150, 230, 0.4)' } },
    axisLabel: { ...AXIS_LABEL, color: '#d6ebff', fontSize: 15 }
  },
  yAxis: [
    {
      type: 'value',
      name: '人',
      nameTextStyle: { color: '#7fa6cc', fontSize: 13 },
      axisLabel: { ...AXIS_LABEL, formatter: toWan },
      splitLine: SPLIT_LINE
    },
    {
      type: 'value',
      name: '元',
      nameTextStyle: { color: '#7fa6cc', fontSize: 13 },
      axisLabel: { ...AXIS_LABEL, formatter: toWan },
      splitLine: { show: false }
    }
  ],
  series: [
    {
      name: '人员数量',
      type: 'bar',
      barWidth: 26,
      data: cityData.value.map(c => c.count),
      itemStyle: { color: vGrad('#33d6ff', 'rgba(31, 124, 255, 0.15)'), borderRadius: [4, 4, 0, 0] },
      emphasis: { itemStyle: { color: vGrad('#ffe28a', 'rgba(255, 197, 61, 0.2)') } },
      cursor: 'pointer'
    },
    {
      name: '人均年收入',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      symbol: 'circle',
      symbolSize: 9,
      data: cityData.value.map(c => c.avg_income),
      lineStyle: { color: '#ffc53d', width: 3, shadowColor: 'rgba(255, 197, 61, 0.6)', shadowBlur: 10 },
      itemStyle: { color: '#ffc53d', borderColor: '#fff4d0', borderWidth: 2 }
    }
  ]
}))

const genderOption = computed(() => {
  const k = kpi.value
  return {
    tooltip: { ...TOOLTIP, trigger: 'item', formatter: (p) => `${p.marker}${p.name}：${p.value.toLocaleString()} 人（${p.percent}%）` },
    title: {
      text: `${k.male_ratio || 0}% : ${k.female_ratio || 0}%`,
      subtext: '男 : 女',
      left: '37%',
      top: '38%',
      textAlign: 'center',
      textStyle: { color: '#ffffff', fontSize: 22, fontWeight: 700 },
      subtextStyle: { color: '#9cc3e6', fontSize: 14 }
    },
    legend: {
      orient: 'vertical',
      right: 6,
      top: 'middle',
      itemGap: 22,
      textStyle: { color: '#d6ebff', fontSize: 15 },
      formatter: (name) => `${name}  ${name === '男性' ? (k.male_count || 0).toLocaleString() : (k.female_count || 0).toLocaleString()}`
    },
    series: [{
      type: 'pie',
      center: ['37%', '50%'],
      radius: ['58%', '78%'],
      startAngle: 90,
      padAngle: 2,
      label: { show: false },
      itemStyle: { borderRadius: 4 },
      data: [
        { name: '男性', value: k.male_count || 0, itemStyle: { color: vGrad('#5ca8ff', '#1f5fd6') } },
        { name: '女性', value: k.female_count || 0, itemStyle: { color: vGrad('#ff8cc0', '#d63a86') } }
      ]
    }]
  }
})

const INCOME_COLORS = ['#1f7cff', '#33d6ff', '#36e2a0', '#ffc53d', '#ff8a3d', '#ff4d6d']
const incomeOption = computed(() => ({
  tooltip: { ...TOOLTIP, trigger: 'item', formatter: (p) => `${p.marker}${p.name}：${p.value.toLocaleString()} 人（${p.percent}%）` },
  legend: {
    orient: 'vertical',
    right: 4,
    top: 'middle',
    itemGap: 10,
    itemWidth: 12,
    itemHeight: 12,
    textStyle: { color: '#d6ebff', fontSize: 14 },
    formatter: (name) => {
      const total = incomeData.value.reduce((s, d) => s + d.count, 0) || 1
      const hit = incomeData.value.find(d => d.bracket === name)
      return `${name}  ${hit ? (hit.count / total * 100).toFixed(1) : 0}%`
    }
  },
  series: [{
    type: 'pie',
    roseType: 'radius',
    center: ['36%', '52%'],
    radius: ['18%', '82%'],
    label: { show: false },
    itemStyle: { borderRadius: 4, borderColor: 'rgba(5, 22, 56, 0.9)', borderWidth: 2 },
    data: incomeData.value.map((d, i) => ({ name: d.bracket, value: d.count, itemStyle: { color: INCOME_COLORS[i % INCOME_COLORS.length] } }))
  }]
}))

const onCityClick = (params) => {
  const city = cityData.value[params.dataIndex]?.city
  if (city) emit('drill-city', city)
}

// ---------------- 生命周期 ----------------
const timers = []
onMounted(() => {
  fitScreen()
  window.addEventListener('resize', fitScreen)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  updateClock()
  fetchStats()
  fetchSystemStatus()
  fetchAudit()
  timers.push(setInterval(updateClock, 1000))
  timers.push(setInterval(fetchAudit, 10 * 1000))
  timers.push(setInterval(() => { fetchStats(); fetchSystemStatus() }, 5 * 60 * 1000))
})

onUnmounted(() => {
  window.removeEventListener('resize', fitScreen)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  timers.forEach(clearInterval)
})

defineExpose({ refresh: () => { fetchStats(); fetchSystemStatus(); fetchAudit() } })
</script>

<style scoped>
.screen-stage {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: #020b1f;
}

.screen-canvas {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center center;
  display: flex;
  flex-direction: column;
  color: #e8f4ff;
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', 'Source Han Sans SC', sans-serif;
  background:
    radial-gradient(ellipse 60% 45% at 50% 38%, rgba(20, 90, 200, 0.28), transparent 70%),
    linear-gradient(rgba(40, 120, 255, 0.05) 1px, transparent 1px) 0 0 / 40px 40px,
    linear-gradient(90deg, rgba(40, 120, 255, 0.05) 1px, transparent 1px) 0 0 / 40px 40px,
    linear-gradient(180deg, #041330 0%, #030d24 100%);
}

/* ---------- 标题栏 ---------- */
.screen-header {
  position: relative;
  height: 100px;
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0 28px;
}
.header-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
.header-title {
  position: absolute;
  left: 50%;
  top: 4px;
  transform: translateX(-50%);
  text-align: center;
}
.header-title h1 {
  font-size: 42px;
  font-weight: 800;
  line-height: 50px;
  letter-spacing: 10px;
  background: linear-gradient(180deg, #ffffff 30%, #8fd8ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 0 12px rgba(51, 180, 255, 0.55));
  white-space: nowrap;
}
.header-title p {
  font-size: 11px;
  line-height: 16px;
  letter-spacing: 4px;
  color: rgba(143, 216, 255, 0.6);
}
.header-side {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  height: 56px;
}
.clock-time {
  font-family: 'Bahnschrift', 'DIN Alternate', 'Consolas', monospace;
  font-size: 34px;
  font-weight: 700;
  color: #5ce1ff;
  text-shadow: 0 0 10px rgba(51, 214, 255, 0.6);
  font-variant-numeric: tabular-nums;
}
.clock-date {
  font-size: 14px;
  line-height: 1.35;
  color: #b8d6f2;
}
.sec-badge {
  padding: 5px 12px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #ff7875;
  border: 1px solid rgba(255, 77, 79, 0.7);
  background: rgba(120, 10, 20, 0.35);
}
.hdr-btn {
  padding: 6px 16px;
  font-size: 15px;
  color: #cfe8ff;
  border: 1px solid rgba(51, 214, 255, 0.45);
  background: linear-gradient(180deg, rgba(20, 80, 170, 0.55), rgba(8, 36, 90, 0.55));
  transition: all 0.2s;
}
.hdr-btn:hover {
  color: #fff;
  border-color: #33d6ff;
  box-shadow: 0 0 12px rgba(51, 214, 255, 0.5);
}

/* ---------- 主体 ---------- */
.screen-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 500px 1fr 500px;
  gap: 18px;
  padding: 8px 22px 22px;
}
.col {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

/* 核心指标 */
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: repeat(3, 1fr);
  gap: 10px;
  height: 100%;
}
.kpi-tile {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 16px;
  border-left: 3px solid #33d6ff;
  background: linear-gradient(90deg, rgba(31, 124, 255, 0.22), rgba(31, 124, 255, 0.03));
}
.kpi-label {
  font-size: 15px;
  color: #9cc3e6;
}
.kpi-value {
  margin-top: 2px;
  font-family: 'Bahnschrift', 'DIN Alternate', 'Consolas', monospace;
  font-size: 30px;
  font-weight: 700;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.kpi-value small {
  margin-left: 4px;
  font-family: 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #9cc3e6;
}

.legend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #b8d6f2;
}
.legend i {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-left: 8px;
  border-radius: 2px;
}

/* 中央总量 */
.hero {
  height: 230px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.hero-label {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #cfe8ff;
}
.hero-label span {
  font-size: 16px;
  font-weight: 400;
  letter-spacing: 0;
  color: #7fa6cc;
}
.hero-stats {
  display: flex;
  gap: 12px;
  white-space: nowrap;
}
.hero-stats > div {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 14px;
  border: 1px solid rgba(51, 214, 255, 0.25);
  background: rgba(10, 50, 120, 0.35);
}
.hero-stats span {
  font-size: 14px;
  color: #9cc3e6;
}
.hero-stats b {
  font-family: 'Bahnschrift', 'DIN Alternate', 'Consolas', monospace;
  font-size: 24px;
  color: #5ce1ff;
  font-variant-numeric: tabular-nums;
}
.hero-stats em {
  font-style: normal;
  font-size: 13px;
  color: #9cc3e6;
}

/* 城市排行 */
.rank-head,
.rank-row {
  display: grid;
  grid-template-columns: 48px 1fr 110px 70px;
  align-items: center;
  gap: 10px;
}
.rank-head {
  padding: 0 8px 8px;
  font-size: 14px;
  color: #7fa6cc;
  border-bottom: 1px solid rgba(51, 214, 255, 0.2);
}
.rank-scroll {
  height: calc(100% - 32px);
}
.fade-edges {
  -webkit-mask-image: linear-gradient(180deg, transparent 0, #000 6%, #000 94%, transparent 100%);
  mask-image: linear-gradient(180deg, transparent 0, #000 6%, #000 94%, transparent 100%);
}
.rank-row {
  height: 52px;
  padding: 0 8px;
  cursor: pointer;
  border-bottom: 1px dashed rgba(80, 150, 230, 0.15);
  transition: background 0.2s;
}
.rank-row:hover {
  background: rgba(51, 214, 255, 0.08);
}
.rank-no {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Bahnschrift', 'Consolas', monospace;
  font-size: 17px;
  font-weight: 700;
  clip-path: polygon(50% 0, 100% 25%, 100% 75%, 50% 100%, 0 75%, 0 25%);
}
.rank-1 { background: linear-gradient(180deg, #ffe28a, #d99a00); color: #3a2600; }
.rank-2 { background: linear-gradient(180deg, #e6f0ff, #8ea9c8); color: #1a2a40; }
.rank-3 { background: linear-gradient(180deg, #ffc69a, #c46a2a); color: #3a1a00; }
.rank-4 { background: rgba(31, 124, 255, 0.35); color: #cfe8ff; }
.rank-city {
  font-size: 17px;
  color: #e8f4ff;
}
.rank-bar {
  margin-top: 5px;
  height: 6px;
  background: rgba(31, 124, 255, 0.15);
}
.rank-bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #1f7cff, #33d6ff);
  box-shadow: 0 0 6px rgba(51, 214, 255, 0.6);
}
.rank-count {
  text-align: right;
  font-family: 'Bahnschrift', 'Consolas', monospace;
  font-size: 19px;
  color: #5ce1ff;
  font-variant-numeric: tabular-nums;
}
.rank-share {
  text-align: right;
  font-family: 'Bahnschrift', 'Consolas', monospace;
  font-size: 16px;
  color: #ffd76a;
}

/* 审计动态 */
.audit-row {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  font-size: 15px;
  border-bottom: 1px dashed rgba(80, 150, 230, 0.15);
}
.audit-time {
  font-family: 'Bahnschrift', 'Consolas', monospace;
  color: #7fa6cc;
  font-variant-numeric: tabular-nums;
}
.audit-tag {
  flex-shrink: 0;
  padding: 1px 8px;
  font-size: 13px;
  border: 1px solid;
}
.tag-search { color: #5ce1ff; border-color: rgba(51, 214, 255, 0.5); background: rgba(51, 214, 255, 0.1); }
.tag-view { color: #ffc53d; border-color: rgba(255, 197, 61, 0.5); background: rgba(255, 197, 61, 0.1); }
.audit-text {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: #d6ebff;
}
.audit-empty {
  padding-top: 60px;
  text-align: center;
  color: #7fa6cc;
}
</style>
