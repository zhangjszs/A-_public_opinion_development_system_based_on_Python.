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
      background-color="#001529"
      text-color="#fff"
      active-text-color="#1890ff"
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
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  overflow: hidden;
  
  .logo {
    height: 40px;
    width: auto;
    flex-shrink: 0;
  }
  
  .title {
    margin-left: 10px;
    font-size: 16px;
    font-weight: bold;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
  }
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
  }
  
  :deep(.el-menu-item) {
    &:hover {
      background-color: #1890ff !important;
    }
    
    &.is-active {
      background-color: #1890ff !important;
    }
  }
}
</style>
