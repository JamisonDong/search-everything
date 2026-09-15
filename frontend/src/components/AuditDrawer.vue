<template>
  <div 
    v-if="visible" 
    class="fixed inset-0 z-50 flex items-center justify-start bg-black/60 backdrop-blur-sm transition-opacity"
    @click.self="emit('close')"
  >
    <div 
      class="h-full w-full max-w-lg bg-command-card border-r border-command-border shadow-2xl p-6 overflow-y-auto flex flex-col justify-between animate-in slide-in-from-left duration-300"
    >
      <div>
        <div class="flex items-center justify-between border-b border-slate-700/80 pb-4">
          <div class="flex items-center gap-2">
            <span class="text-emerald-400">🛡️</span>
            <h3 class="text-lg font-bold text-white tracking-wide">涉密安全操作审计日志</h3>
          </div>
          <button 
            @click="emit('close')" 
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            ✕
          </button>
        </div>

        <div class="mt-4 flex items-center justify-between text-xs text-slate-400">
          <span>记录最近 50 条单机操作轨迹 (不可逆审计)</span>
          <button 
            @click="fetchLogs" 
            class="rounded px-2 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 font-medium"
          >
            🔄 刷新日志
          </button>
        </div>

        <div class="mt-4 space-y-3">
          <div 
            v-for="(log, idx) in logs" 
            :key="idx" 
            class="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs space-y-1 hover:border-slate-700 transition"
          >
            <div class="flex items-center justify-between font-mono">
              <span 
                :class="{
                  'bg-cyan-950 text-cyan-400 border-cyan-800': log.action === 'SEARCH',
                  'bg-amber-950 text-amber-400 border-amber-800': log.action === 'VIEW_DETAIL',
                  'bg-rose-950 text-rose-400 border-rose-800': log.action === 'EXPORT_ATTEMPT'
                }"
                class="rounded border px-1.5 py-0.5 font-bold text-[10px]"
              >
                {{ log.action }}
              </span>
              <span class="text-slate-400 text-[11px]">{{ formatTime(log.timestamp) }}</span>
            </div>
            <div class="flex items-center gap-3 text-slate-300 text-[11px]">
              <span>操作员: <span class="text-white font-medium">{{ log.operator }}</span></span>
              <span>终端: <span class="text-cyan-300 font-mono">{{ log.terminal_id }}</span></span>
              <span>IP: <span class="text-slate-400 font-mono">{{ log.client_ip }}</span></span>
            </div>
            <div class="mt-1 bg-slate-950/60 p-2 rounded text-[11px] text-slate-400 font-mono break-all">
              <div v-if="log.action === 'SEARCH'">
                关键词: <span class="text-cyan-200">{{ log.details.keyword || '(空/全部)' }}</span> | 
                城市: {{ log.details.city || '不限' }} | 
                命中: <span class="text-emerald-400">{{ log.details.total_hits?.toLocaleString() }}</span> 条 |
                耗时: {{ log.details.query_cost_ms }}ms
              </div>
              <div v-else-if="log.action === 'VIEW_DETAIL'">
                调阅人员证件: <span class="text-amber-300">{{ log.details.person_id }}</span> (已记录操作行为)
              </div>
              <div v-else>
                {{ JSON.stringify(log.details) }}
              </div>
            </div>
          </div>

          <div v-if="logs.length === 0" class="py-12 text-center text-slate-500 text-xs">
            暂无审计记录
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['close'])

const logs = ref([])

const fetchLogs = async () => {
  try {
    const res = await fetch('/api/audit/logs?limit=50')
    logs.value = await res.json()
  } catch (e) {
    console.error('Failed to fetch audit logs:', e)
  }
}

const formatTime = (ts) => {
  if (!ts) return ''
  return ts.replace('T', ' ').substring(0, 19)
}

onMounted(() => {
  fetchLogs()
})
</script>
