<template>
  <div>
    <!-- 防拍照屏幕溯源水印 (大屏与检索工作台共用) -->
    <WatermarkOverlay
      :visible="watermarkEnabled"
      :operator="currentOperator"
      :terminal-id="terminalId"
    />

    <!-- 态势大屏：仅展示聚合统计，不含个人明细，适合领导汇报与指挥大屏展示 -->
    <DashboardScreen
      v-show="view === 'screen'"
      @open-search="view = 'search'"
      @open-audit="auditDrawerVisible = true"
      @drill-city="drillCity"
      @cities-loaded="cityList = $event"
    />

    <!-- 检索工作台：人员明细检索、档案调阅 -->
    <SearchWorkbench
      v-show="view === 'search'"
      ref="workbench"
      v-model:mask-sensitive="maskSensitive"
      v-model:watermark-enabled="watermarkEnabled"
      :operator="currentOperator"
      :cities="cityList"
      @open-audit="auditDrawerVisible = true"
      @back="view = 'screen'"
    />

    <!-- 安全审计日志抽屉 -->
    <AuditDrawer
      v-if="auditDrawerVisible"
      :visible="auditDrawerVisible"
      @close="auditDrawerVisible = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import WatermarkOverlay from './components/WatermarkOverlay.vue'
import AuditDrawer from './components/AuditDrawer.vue'
import DashboardScreen from './views/DashboardScreen.vue'
import SearchWorkbench from './views/SearchWorkbench.vue'

const view = ref('screen')
const watermarkEnabled = ref(true)
const maskSensitive = ref(false)
const auditDrawerVisible = ref(false)
const cityList = ref([])

const currentOperator = ref('涉密警员-01')
const terminalId = ref('SEC-LOCAL-PC')

const workbench = ref(null)

// 大屏点击城市 → 切换到检索工作台并按城市筛选
const drillCity = (city) => {
  view.value = 'search'
  workbench.value?.searchByCity(city)
}
</script>
