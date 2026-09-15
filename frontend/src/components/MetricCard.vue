<template>
  <div 
    class="relative overflow-hidden rounded-xl border border-command-border bg-command-card/80 p-5 backdrop-blur-md transition-all duration-300 hover:border-command-cyan/50 hover:shadow-glow-cyan group"
  >
    <!-- 顶部微弱高光边框 -->
    <div class="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-400/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
    
    <div class="flex items-center justify-between">
      <span class="text-xs font-semibold tracking-wider text-slate-400 uppercase">{{ title }}</span>
      <div 
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700/60 bg-slate-800/60 text-cyan-400 shadow-inner group-hover:scale-110 transition-transform"
      >
        <slot name="icon"></slot>
      </div>
    </div>

    <div class="mt-3 flex items-baseline gap-2">
      <div class="text-3xl font-extrabold tracking-tight text-white font-mono">
        {{ formattedValue }}
      </div>
      <span v-if="unit" class="text-xs font-medium text-slate-400">{{ unit }}</span>
    </div>

    <div class="mt-2 flex items-center gap-2 text-xs text-slate-400">
      <span class="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
      <span>{{ subtitle }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: [Number, String],
  unit: String,
  subtitle: String,
  accent: {
    type: String,
    default: 'cyan'
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value || '0'
})
</script>
