<template>
  <div class="relative min-h-screen bg-command-bg text-slate-100 tech-grid-bg pb-12">
    <!-- 顶部指挥中心状态栏 -->
    <header class="sticky top-0 z-40 border-b border-command-border bg-command-bg/90 backdrop-blur-md px-6 py-3 shadow-lg">
      <div class="flex items-center justify-between">
        <!-- 标题与密级标 -->
        <div class="flex items-center gap-4">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-700 text-white shadow-glow-cyan">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-xl font-black tracking-wider text-white">
                人员信息检索工作台
              </h1>
              <span class="rounded bg-red-950/80 border border-red-500/80 px-2 py-0.5 text-xs font-bold text-red-400 tracking-widest animate-pulse">
                涉密专机 · 严禁外联
              </span>
            </div>
            <div class="flex items-center gap-4 text-xs text-slate-400 mt-0.5 font-mono">
              <span>引擎: <strong class="text-cyan-400">DuckDB 列存向量化</strong></span>
              <span>数据量级: <strong class="text-emerald-400">1600万级就绪</strong></span>
              <span>部署模式: 纯单机物理隔离</span>
            </div>
          </div>
        </div>

        <!-- 右侧控制区 -->
        <div class="flex items-center gap-3">
          <!-- 当前时钟 -->
          <div class="hidden lg:flex flex-col items-end text-xs font-mono text-slate-400 mr-2">
            <span class="text-slate-200 font-semibold">{{ currentTime }}</span>
            <span class="text-[10px] text-emerald-400">● 单机内网离线运行</span>
          </div>

          <!-- 一键脱敏开关 -->
          <button 
            @click="toggleMasking" 
            :class="maskSensitive ? 'bg-amber-900/60 border-amber-500 text-amber-300' : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:text-white'"
            class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition shadow-sm"
          >
            <span>{{ maskSensitive ? '🔒 脱敏模式 (已生效)' : '🔓 原始明文模式' }}</span>
          </button>

          <!-- 水印开关 -->
          <button
            @click="emit('update:watermarkEnabled', !watermarkEnabled)"
            :class="watermarkEnabled ? 'bg-cyan-950/60 border-cyan-500 text-cyan-300' : 'bg-slate-800/80 border-slate-700 text-slate-400'"
            class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition shadow-sm"
          >
            <span>{{ watermarkEnabled ? '👁️ 防拍水印已开启' : '👁️ 防拍水印关闭' }}</span>
          </button>

          <!-- 审计日志按钮 -->
          <button
            @click="emit('open-audit')"
            class="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition shadow-sm"
          >
            <span>🛡️ 安全审计</span>
          </button>

          <!-- 返回态势大屏 -->
          <button
            @click="emit('back')"
            class="flex items-center gap-1.5 rounded-lg border border-cyan-500/40 bg-cyan-950/40 px-3 py-1.5 text-xs font-medium text-cyan-400 hover:bg-cyan-900/50 transition shadow-sm"
          >
            <span>📊 返回态势大屏</span>
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-[1780px] px-6 pt-6 space-y-6">
      <!-- 3. 多维智能组合搜索工作台 -->
      <div class="rounded-xl border border-command-border bg-command-card/90 p-5 shadow-xl space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="flex h-3 w-3 items-center justify-center rounded-full bg-cyan-500">
              <span class="h-1.5 w-1.5 rounded-full bg-white"></span>
            </span>
            <h2 class="text-base font-bold text-white tracking-wide">人员信息多维智能检索工作台</h2>
          </div>
          <div class="text-xs text-slate-400 font-mono">
            支持拼音、姓名、外文全称、18位证件号、街道门牌多维索引秒级匹配
          </div>
        </div>

        <!-- 主检索栏与快捷过滤条 -->
        <div class="grid grid-cols-1 md:grid-cols-12 gap-3">
          <!-- 主关键词输入 -->
          <div class="md:col-span-6 relative">
            <input 
              v-model="searchParams.keyword" 
              @keyup.enter="doSearch(1)"
              placeholder="搜索姓名、外文名字 (如 David)、身份证号、或地址关键词 (如 中关村)..." 
              class="w-full rounded-lg border border-slate-700 bg-slate-900/90 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 font-mono transition"
            />
            <div class="absolute left-3.5 top-3 text-slate-500">
              🔍
            </div>
            <button 
              v-if="searchParams.keyword" 
              @click="searchParams.keyword = ''; doSearch(1)" 
              class="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-white"
            >
              ✕
            </button>
          </div>

          <!-- 城市筛选 -->
          <div class="md:col-span-2">
            <select 
              v-model="searchParams.city" 
              @change="doSearch(1)"
              class="w-full rounded-lg border border-slate-700 bg-slate-900/90 py-2.5 px-3 text-sm text-slate-200 focus:border-cyan-400 focus:outline-none transition"
            >
              <option value="">全部城市 (不限)</option>
              <option v-for="c in cityList" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <!-- 性别筛选 -->
          <div class="md:col-span-2">
            <select 
              v-model="searchParams.gender" 
              @change="doSearch(1)"
              class="w-full rounded-lg border border-slate-700 bg-slate-900/90 py-2.5 px-3 text-sm text-slate-200 focus:border-cyan-400 focus:outline-none transition"
            >
              <option value="">性别: 不限</option>
              <option value="男">男 (Male)</option>
              <option value="女">女 (Female)</option>
            </select>
          </div>

          <!-- 搜索与重置按钮 -->
          <div class="md:col-span-2 flex items-center gap-2">
            <button 
              @click="doSearch(1)" 
              :disabled="searching"
              class="flex-1 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 py-2.5 text-center text-sm font-semibold text-white shadow-glow-cyan hover:from-cyan-500 hover:to-blue-500 transition disabled:opacity-50"
            >
              <span v-if="searching">检索中...</span>
              <span v-else>立即检索</span>
            </button>
            <button 
              @click="resetSearch" 
              class="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm font-medium text-slate-400 hover:bg-slate-700 hover:text-white transition"
              title="重置所有条件"
            >
              重置
            </button>
          </div>
        </div>

        <!-- 次级过滤器 (年龄段、年收入段、排序字段) -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs border-t border-slate-800/80">
          <div class="flex flex-wrap items-center gap-4">
            <!-- 年龄段快捷选 -->
            <div class="flex items-center gap-2">
              <span class="text-slate-400">年龄区间:</span>
              <div class="flex items-center gap-1">
                <input 
                  type="number" 
                  v-model.number="searchParams.min_age" 
                  placeholder="最小" 
                  class="w-16 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-center text-white"
                  @change="doSearch(1)"
                />
                <span class="text-slate-500">-</span>
                <input 
                  type="number" 
                  v-model.number="searchParams.max_age" 
                  placeholder="最大" 
                  class="w-16 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-center text-white"
                  @change="doSearch(1)"
                />
                <span class="text-slate-500">岁</span>
              </div>
            </div>

            <!-- 年收入区间 -->
            <div class="flex items-center gap-2">
              <span class="text-slate-400">年收入区间:</span>
              <div class="flex items-center gap-1">
                <input 
                  type="number" 
                  v-model.number="searchParams.min_income" 
                  placeholder="最低" 
                  class="w-20 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-center text-white"
                  @change="doSearch(1)"
                />
                <span class="text-slate-500">-</span>
                <input 
                  type="number" 
                  v-model.number="searchParams.max_income" 
                  placeholder="最高" 
                  class="w-20 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-center text-white"
                  @change="doSearch(1)"
                />
                <span class="text-slate-500">元</span>
              </div>
            </div>

            <!-- 排序方式 -->
            <div class="flex items-center gap-2">
              <span class="text-slate-400">排序依据:</span>
              <select 
                v-model="searchParams.order_by" 
                @change="doSearch(1)"
                class="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-slate-200"
              >
                <option value="annual_income">按年收入 (高到低)</option>
                <option value="age">按年龄大小</option>
                <option value="id">按证件编号</option>
                <option value="name">按姓名顺序</option>
              </select>
            </div>
          </div>

          <!-- 检索性能与结果统计 -->
          <div class="flex items-center gap-3 font-mono text-slate-400">
            <span>匹配条数: <strong class="text-cyan-400 font-bold">{{ searchResults.total?.toLocaleString() || 0 }}</strong> 条</span>
            <span class="text-slate-600">|</span>
            <span>检索耗时: <strong class="text-emerald-400">{{ searchResults.query_cost_ms || 0 }}</strong> ms</span>
          </div>
        </div>

        <!-- 4. 高性能检索结果表格 -->
        <div class="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/40">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th class="py-3 px-3">序号</th>
                <th class="py-3 px-3">证件编码 (ID)</th>
                <th class="py-3 px-3">姓名 / 性别</th>
                <th class="py-3 px-3">外文名字 / 性别</th>
                <th class="py-3 px-3">年龄</th>
                <th class="py-3 px-3">常住城市</th>
                <th class="py-3 px-3">详细登记地址</th>
                <th class="py-3 px-3 text-right">申报年收入</th>
                <th class="py-3 px-3 text-center">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 font-mono">
              <tr 
                v-for="(item, index) in searchResults.items" 
                :key="item.id + index"
                class="hover:bg-slate-800/40 transition-colors group"
              >
                <td class="py-2.5 px-3 text-slate-500 font-mono">
                  {{ (searchResults.page - 1) * searchResults.page_size + index + 1 }}
                </td>
                <td class="py-2.5 px-3 font-mono font-medium text-cyan-300">
                  {{ item.id }}
                </td>
                <td class="py-2.5 px-3">
                  <div class="flex items-center gap-1.5">
                    <span class="font-sans font-bold text-white">{{ item.name }}</span>
                    <span 
                      :class="item.gender === '男' ? 'text-blue-400 bg-blue-950/80 border-blue-800' : 'text-pink-400 bg-pink-950/80 border-pink-800'"
                      class="rounded border px-1 py-0.2 text-[10px]"
                    >
                      {{ item.gender }}
                    </span>
                  </div>
                </td>
                <td class="py-2.5 px-3 text-slate-400 font-mono">
                  {{ item.foreign_name || '-' }} <span class="text-[10px] text-slate-500">({{ item.foreign_gender }})</span>
                </td>
                <td class="py-2.5 px-3 text-slate-300">
                  {{ item.age }} 岁
                </td>
                <td class="py-2.5 px-3 text-cyan-200">
                  {{ item.city }}
                </td>
                <td class="py-2.5 px-3 text-slate-400 max-w-xs truncate font-sans" :title="item.address">
                  {{ item.address }}
                </td>
                <td class="py-2.5 px-3 text-right font-bold text-amber-400">
                  {{ item.income_display }}
                </td>
                <td class="py-2.5 px-3 text-center">
                  <button 
                    @click="viewDetail(item.id, item.raw_id)"
                    class="rounded border border-cyan-500/40 bg-cyan-950/40 px-2.5 py-1 text-[11px] font-medium text-cyan-300 hover:bg-cyan-800/60 hover:text-white transition shadow-sm"
                  >
                    全景档案
                  </button>
                </td>
              </tr>

              <tr v-if="!searchResults.items || searchResults.items.length === 0">
                <td colspan="9" class="py-12 text-center text-slate-500">
                  <div class="text-sm">未匹配到符合条件的人员记录</div>
                  <div class="text-xs text-slate-600 mt-1">请尝试调整搜索关键词或扩大筛选范围</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 5. 高性能分页导航条 -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-slate-400">
          <div class="flex items-center gap-2">
            <span>每页显示:</span>
            <select 
              v-model.number="searchParams.page_size" 
              @change="doSearch(1)"
              class="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-slate-200"
            >
              <option :value="20">20 条/页</option>
              <option :value="50">50 条/页</option>
              <option :value="100">100 条/页</option>
            </select>
            <span class="ml-2 font-mono">
              第 {{ searchResults.page }} / {{ searchResults.total_pages || 1 }} 页
            </span>
          </div>

          <!-- 分页按钮 -->
          <div class="flex items-center gap-1 font-mono">
            <button 
              @click="doSearch(1)" 
              :disabled="searchResults.page <= 1"
              class="rounded border border-slate-800 bg-slate-900 px-2.5 py-1 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900"
            >
              首页
            </button>
            <button 
              @click="doSearch(searchResults.page - 1)" 
              :disabled="searchResults.page <= 1"
              class="rounded border border-slate-800 bg-slate-900 px-2.5 py-1 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900"
            >
              上一页
            </button>
            <span class="px-2 font-bold text-cyan-400">{{ searchResults.page }}</span>
            <button 
              @click="doSearch(searchResults.page + 1)" 
              :disabled="searchResults.page >= searchResults.total_pages"
              class="rounded border border-slate-800 bg-slate-900 px-2.5 py-1 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900"
            >
              下一页
            </button>
            <button 
              @click="doSearch(searchResults.total_pages)" 
              :disabled="searchResults.page >= searchResults.total_pages"
              class="rounded border border-slate-800 bg-slate-900 px-2.5 py-1 text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-slate-900"
            >
              末页
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 人员全景档案抽屉模态框 -->
    <PersonnelModal 
      :visible="modalVisible" 
      :person="selectedPerson" 
      @close="modalVisible = false" 
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import PersonnelModal from '../components/PersonnelModal.vue'

const props = defineProps({
  maskSensitive: { type: Boolean, default: false },
  watermarkEnabled: { type: Boolean, default: true },
  operator: { type: String, required: true },
  // 由态势大屏加载后传入的城市列表
  cities: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:maskSensitive', 'update:watermarkEnabled', 'open-audit', 'back'])

const modalVisible = ref(false)
const selectedPerson = ref(null)
const currentTime = ref('')
const searching = ref(false)

const cityList = ref([
  "北京市", "上海市", "广州市", "深圳市", "成都市", 
  "杭州市", "武汉市", "西安市", "南京市", "重庆市", 
  "苏州市", "天津市", "长沙市", "青岛市", "郑州市"
])
watch(() => props.cities, (list) => {
  if (list && list.length) cityList.value = list
}, { immediate: true })

// 搜索参数
const searchParams = reactive({
  keyword: '',
  city: '',
  gender: '',
  min_age: null,
  max_age: null,
  min_income: null,
  max_income: null,
  order_by: 'annual_income',
  order_dir: 'desc',
  page: 1,
  page_size: 20
})

// 搜索结果
const searchResults = ref({
  total: 0,
  page: 1,
  page_size: 20,
  total_pages: 0,
  query_cost_ms: 0,
  items: []
})

// 实时时钟
let timeTimer = null
const updateClock = () => {
  const now = new Date()
  currentTime.value = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`
}

// 执行多维检索
const doSearch = async (targetPage = 1) => {
  searching.value = true
  searchParams.page = targetPage

  const params = new URLSearchParams()
  if (searchParams.keyword) params.append('keyword', searchParams.keyword)
  if (searchParams.city) params.append('city', searchParams.city)
  if (searchParams.gender) params.append('gender', searchParams.gender)
  if (searchParams.min_age !== null && searchParams.min_age !== '') params.append('min_age', searchParams.min_age)
  if (searchParams.max_age !== null && searchParams.max_age !== '') params.append('max_age', searchParams.max_age)
  if (searchParams.min_income !== null && searchParams.min_income !== '') params.append('min_income', searchParams.min_income)
  if (searchParams.max_income !== null && searchParams.max_income !== '') params.append('max_income', searchParams.max_income)
  params.append('order_by', searchParams.order_by)
  params.append('order_dir', searchParams.order_dir)
  params.append('page', searchParams.page)
  params.append('page_size', searchParams.page_size)
  params.append('mask_sensitive', props.maskSensitive ? 'true' : 'false')
  params.append('operator', props.operator)

  try {
    const res = await fetch(`/api/search?${params.toString()}`)
    const data = await res.json()
    searchResults.value = data
  } catch (err) {
    console.error('Search failed:', err)
  } finally {
    searching.value = false
  }
}

// 重置检索条件
const resetSearch = () => {
  searchParams.keyword = ''
  searchParams.city = ''
  searchParams.gender = ''
  searchParams.min_age = null
  searchParams.max_age = null
  searchParams.min_income = null
  searchParams.max_income = null
  searchParams.order_by = 'annual_income'
  searchParams.order_dir = 'desc'
  doSearch(1)
}

// 态势大屏点击城市下钻：带入城市条件直接检索
const searchByCity = (city) => {
  searchParams.city = city
  doSearch(1)
}

// 查看个人全景档案
const viewDetail = async (id, rawId) => {
  const targetId = rawId || id
  try {
    const res = await fetch(`/api/personnel/${encodeURIComponent(targetId)}?mask_sensitive=${props.maskSensitive}&operator=${encodeURIComponent(props.operator)}`)
    if (res.ok) {
      selectedPerson.value = await res.json()
      modalVisible.value = true
    } else {
      alert('未检索到该人员档案信息')
    }
  } catch (err) {
    console.error('Failed to fetch personnel detail:', err)
  }
}

// 切换脱敏模式
const toggleMasking = () => {
  emit('update:maskSensitive', !props.maskSensitive)
}
watch(() => props.maskSensitive, () => doSearch(searchResults.value.page))

onMounted(() => {
  updateClock()
  timeTimer = setInterval(updateClock, 1000)
  doSearch(1)
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
})

defineExpose({ searchByCity })
</script>
