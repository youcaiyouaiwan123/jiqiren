<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  // 当内容已自带卡片（如多分区表单），传 noCard 让 wrapper 不再加白卡片
  noCard?: boolean
}>()
</script>

<template>
  <div class="admin-page">
    <!-- 顶部栏 -->
    <div v-if="title || $slots.tools || $slots.title" class="admin-page-header">
      <div class="admin-page-header-left">
        <slot name="title">
          <div>
            <div class="admin-page-title">{{ title }}</div>
            <div v-if="subtitle" class="admin-page-subtitle">{{ subtitle }}</div>
          </div>
        </slot>
      </div>
      <div v-if="$slots.tools" class="admin-page-tools">
        <slot name="tools" />
      </div>
    </div>

    <!-- 内容 -->
    <div :class="noCard ? 'admin-page-body-bare' : 'admin-page-body'">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
}

.admin-page-header-left { min-width: 0; flex: 1; }
.admin-page-title { font-size: 15px; font-weight: 600; color: #1f2937; }
.admin-page-subtitle { font-size: 12px; color: #94a3b8; margin-top: 2px; }

.admin-page-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.admin-page-body {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.admin-page-body-bare {
  /* 内容自带卡片时，wrapper 不再加边框，但保留间距上下文 */
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
