<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="iconSize" :color="iconColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description">{{ description }}</p>
    <div v-if="$slots.action" class="empty-action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    icon: {
      type: String,
      default: 'Warning',
    },
    iconSize: {
      type: Number,
      default: 64,
    },
    iconColor: {
      type: String,
      default: '#909399',
    },
    title: {
      type: String,
      default: '暂无数据',
    },
    description: {
      type: String,
      default: '',
    },
  })
</script>

<style lang="scss" scoped>
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    text-align: center;
  }

  .empty-icon {
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 500;
    color: #606266;
    margin-bottom: 8px;
  }

  .empty-description {
    font-size: 14px;
    color: #909399;
    margin-bottom: 16px;
    max-width: 300px;
  }

  .empty-action {
    margin-top: 8px;
  }
</style>
