<template>
  <div class="sidebar-container">
    <div class="logo-container">
      <img src="@/assets/images/logo.png" alt="Logo" class="logo" />
      <transition name="fade">
        <span v-if="!collapsed" class="title">微博舆情分析</span>
      </transition>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :collapse-transition="false"
      class="sidebar-menu"
      background-color="#0F172A"
      text-color="#94A3B8"
      active-text-color="#FFFFFF"
      router
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <el-menu-item :index="route.path">
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <template #title>{{ route.meta.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()

const menuRoutes = computed(() => {
  const parentRoute = route.matched.find(r => r.children)?.path
  if (!parentRoute) return []
  
  const parent = route.matched.find(r => r.children && r.children.some(c => c.meta))
  return parent?.children.filter(child => child.meta && !child.meta.public) || []
})

const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #0F172A; // Slate 900
  border-right: 1px solid #1E293B; // Slate 800
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  overflow: hidden;
  border-bottom: 1px solid #1E293B;
  
  .logo {
    height: 32px;
    width: auto;
    flex-shrink: 0;
  }
  
  .title {
    margin-left: 12px;
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    white-space: nowrap;
    overflow: hidden;
    letter-spacing: 0.5px;
  }
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  border-right: none;
  padding-top: 8px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }
  
  :deep(.el-menu-item) {
    margin: 4px 8px;
    height: 44px;
    line-height: 44px;
    border-radius: 6px;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.05) !important;
      color: #F8FAFC !important;
    }
    
    &.is-active {
      background-color: $primary-color !important;
      color: #FFFFFF !important;
      font-weight: 500;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .el-icon {
      font-size: 18px;
    }
  }
}
</style>
