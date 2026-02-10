<template>
  <el-config-provider :locale="locale">
    <el-container class="layout-container">
      <el-aside :width="isCollapsed ? '64px' : '240px'" class="sidebar" :class="{ 'is-collapsed': isCollapsed }">
        <Sidebar :collapsed="isCollapsed" />
      </el-aside>
      <el-container>
        <el-header class="header">
          <Header @toggle="toggleSidebar" />
        </el-header>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive>
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const locale = zhCn
const appStore = useAppStore()
const isCollapsed = computed(() => appStore.sidebarCollapsed)

const toggleSidebar = () => {
  appStore.toggleSidebar()
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
  background-color: $background-color;
}

.sidebar {
  background-color: #0F172A; // Slate 900
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
  border-right: 1px solid #1E293B; // Slate 800
  
  &.is-collapsed {
    width: 64px !important;
  }
}

.header {
  padding: 0;
  background: $surface-color;
  box-shadow: $box-shadow-sm;
  height: 64px;
  line-height: 64px;
  flex-shrink: 0;
  z-index: 10;
}

.main-content {
  background: $background-color;
  padding: 24px;
  overflow: auto;
  height: calc(100vh - 64px);
  
  // Custom scrollbar
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #CBD5E1; // Slate 300
    border-radius: 4px;
    
    &:hover {
      background: #94A3B8; // Slate 400
    }
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
}
</style>
