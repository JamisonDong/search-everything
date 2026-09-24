<template>
  <section class="screen-panel">
    <!-- 四角科技框 -->
    <i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>

    <header class="panel-title">
      <span class="title-mark"></span>
      <h3>{{ title }}</h3>
      <span class="title-line"></span>
      <span v-if="extra" class="title-extra">{{ extra }}</span>
      <slot name="extra"></slot>
    </header>

    <div class="panel-body">
      <slot></slot>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  extra: { type: String, default: '' }
})
</script>

<style scoped>
.screen-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 14px 18px 16px;
  background: linear-gradient(180deg, rgba(9, 40, 92, 0.55) 0%, rgba(5, 22, 56, 0.35) 100%);
  border: 1px solid rgba(40, 140, 255, 0.22);
  box-shadow: inset 0 0 28px rgba(0, 120, 255, 0.12);
}

.corner {
  position: absolute;
  width: 14px;
  height: 14px;
  border-color: #33d6ff;
  border-style: solid;
}
.corner.tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.corner.tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
.corner.bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
.corner.br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 34px;
  flex-shrink: 0;
}
.title-mark {
  width: 10px;
  height: 10px;
  transform: rotate(45deg);
  background: linear-gradient(135deg, #5ce1ff, #1f7cff);
  box-shadow: 0 0 8px rgba(51, 214, 255, 0.8);
}
.panel-title h3 {
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #e8f4ff;
  text-shadow: 0 0 10px rgba(51, 180, 255, 0.55);
  white-space: nowrap;
}
.title-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(51, 214, 255, 0.6), rgba(51, 214, 255, 0));
}
.title-extra {
  font-size: 13px;
  color: #7fa6cc;
  white-space: nowrap;
}

.panel-body {
  position: relative;
  flex: 1;
  min-height: 0;
  margin-top: 8px;
}
</style>
