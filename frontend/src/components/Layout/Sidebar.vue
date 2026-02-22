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
  import { useUserStore } from '@/stores/user'

  defineProps({
    collapsed: {
      type: Boolean,
      default: false,
    },
  })

  const route = useRoute()
  const userStore = useUserStore()

  const menuRoutes = computed(() => {
    const parentRoute = route.matched.find((r) => r.children)?.path
    if (!parentRoute) return []

    const parent = route.matched.find((r) => r.children && r.children.some((c) => c.meta))
    const isAdmin = userStore.isAdmin
    return (
      parent?.children.filter((child) => {
        if (!child.meta || child.meta.public) return false
        if (child.meta.adminOnly && !isAdmin) return false
        return true
      }) || []
    )
  })

  const activeMenu = computed(() => route.path)
</script>

<style lang="scss" scoped>
  .sidebar-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: #0f172a; // Slate 900
    border-right: 1px solid #1e293b; // Slate 800
  }

  .logo-container {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    overflow: hidden;
    border-bottom: 1px solid #1e293b;

    .logo {
      height: 32px;
      width: auto;
      flex-shrink: 0;
    }

    .title {
      margin-left: 12px;
      font-size: 16px;
      font-weight: 600;
      color: #f8fafc;
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
        color: #f8fafc !important;
      }

      &.is-active {
        background-color: $primary-color !important;
        color: #ffffff !important;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }

      .el-icon {
        font-size: 18px;
      }
    }
  }
</style>
