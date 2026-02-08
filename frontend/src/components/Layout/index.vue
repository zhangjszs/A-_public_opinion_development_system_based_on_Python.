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
}

.sidebar {
  background-color: #001529;
  transition: width 0.3s ease;
  overflow: hidden;
  flex-shrink: 0;
  
  &.is-collapsed {
    width: 64px !important;
  }
}

.header {
  background: #fff;
  padding: 0;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 60px;
  line-height: 60px;
  flex-shrink: 0;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow: auto;
  height: calc(100vh - 60px);
}
</style>
