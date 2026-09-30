<template>
  <div 
    v-if="visible" 
    class="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm transition-opacity"
    @click.self="emit('close')"
  >
    <div 
      class="h-full w-full max-w-lg bg-command-card border-l border-command-border shadow-2xl p-6 overflow-y-auto flex flex-col justify-between animate-in slide-in-from-right duration-300"
    >
      <div>
        <!-- 抽屉头部 -->
        <div class="flex items-center justify-between border-b border-slate-700/80 pb-4">
          <div class="flex items-center gap-2">
            <div class="h-2 w-2 rounded-full bg-cyan-400 animate-ping"></div>
            <h3 class="text-lg font-bold text-white tracking-wide">人员全景数字档案</h3>
            <span class="rounded bg-red-900/60 border border-red-500/50 px-2 py-0.5 text-[11px] font-semibold text-red-300">
              敏感信息
            </span>
          </div>
          <button 
            @click="emit('close')" 
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
          >
            ✕
          </button>
        </div>

        <!-- 档案核心内容 -->
        <div v-if="person" class="mt-6 space-y-6">
          <!-- 人员头像与主信息 -->
          <div class="flex items-center gap-4 rounded-xl border border-cyan-900/40 bg-slate-900/50 p-4">
            <div class="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-700 text-2xl font-bold text-white shadow-lg font-mono">
              {{ person.name ? person.name[0] : '人' }}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xl font-extrabold text-white">{{ person.name }}</span>
                <span 
                  :class="person.gender === '男' ? 'bg-blue-900/50 text-blue-300 border-blue-700' : 'bg-pink-900/50 text-pink-300 border-pink-700'"
                  class="rounded-full border px-2 py-0.5 text-xs font-semibold"
                >
                  {{ person.gender }}
                </span>
                <span class="text-sm font-mono text-slate-400">{{ person.age }} 岁</span>
              </div>
              <div class="mt-1 text-xs text-slate-400 font-mono">
                证件编码: <span class="text-cyan-300">{{ person.id }}</span>
              </div>
            </div>
          </div>

          <!-- 详细属性网格 -->
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
              <span class="text-xs text-slate-400">外文姓名 (Foreign Name)</span>
              <p class="mt-1 text-sm font-medium text-slate-200 font-mono">{{ person.foreign_name || '未登记' }}</p>
            </div>
            <div class="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
              <span class="text-xs text-slate-400">外文性别 (Gender En)</span>
              <p class="mt-1 text-sm font-medium text-slate-200">{{ person.foreign_gender || 'Unspecified' }}</p>
            </div>
            <div class="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
              <span class="text-xs text-slate-400">常住城市 (City)</span>
              <p class="mt-1 text-sm font-medium text-cyan-300">{{ person.city || '未知' }}</p>
            </div>
            <div class="rounded-lg border border-slate-800 bg-slate-900/40 p-3">
              <span class="text-xs text-slate-400">申报年收入 (Annual Income)</span>
              <p class="mt-1 text-sm font-bold text-amber-400 font-mono">{{ person.income_display }}</p>
            </div>
          </div>

          <!-- 详细住址卡片 -->
          <div class="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div class="flex items-center gap-1.5 text-xs text-slate-400">
              <span>📍 详细登记住址 (Residential Address)</span>
            </div>
            <p class="mt-2 text-sm text-slate-200 font-mono leading-relaxed bg-slate-950/40 p-2.5 rounded border border-slate-800">
              {{ person.address || '未登记具体地址' }}
            </p>
          </div>

          <!-- 档案经济与社会关系画像分析 -->
          <div class="rounded-lg border border-indigo-950/60 bg-indigo-950/20 p-4">
            <div class="text-xs font-semibold text-indigo-400 uppercase tracking-wider">系统研判分析结论</div>
            <ul class="mt-2 space-y-1 text-xs text-slate-300 list-disc list-inside">
              <li>人员常住所属：<span class="text-white">{{ person.city }}</span>，信息核验匹配一致</li>
              <li>收入所属分位：<span class="text-amber-300 font-semibold">{{ person.income_display }}</span></li>
              <li>调阅留痕：本次调阅已写入审计日志，记录操作员工号</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 底部数据安全提醒 -->
      <div class="mt-8 border-t border-slate-800 pt-4">
        <div class="rounded bg-red-950/30 border border-red-900/50 p-3 text-[11px] text-red-400 leading-relaxed">
          ⚠️ <strong>数据安全提醒：</strong> 本系统包含个人敏感信息。每次调阅人员档案均已记录审计日志，严禁擅自拍摄、拷贝或外传。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: Boolean,
  person: Object
})

const emit = defineEmits(['close'])
</script>
