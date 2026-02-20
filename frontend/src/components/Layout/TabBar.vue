<template>
  <div class="tab-bar" @wheel.prevent="onWheel">
    <div class="tab-list" ref="tabListRef">
      <div
        v-for="tab in tabsStore.tabs"
        :key="tab.name"
        class="tab-item"
        :class="{ 'is-active': tab.name === tabsStore.activeTab }"
        @click="handleTabClick(tab)"
        @contextmenu.prevent="showContextMenu($event, tab)"
      >
        <el-icon v-if="tab.icon" class="tab-icon">
          <component :is="tab.icon" />
        </el-icon>
        <span class="tab-title">{{ tab.title }}</span>
        <el-icon
          v-if="tab.closable"
          class="tab-close"
          @click.stop="handleClose(tab.name)"
        >
          <Close />
        </el-icon>
      </div>
    </div>

    <!-- Right-click context menu -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      v-click-outside="hideContextMenu"
    >
      <div class="context-menu-item" @click="closeCurrentTab">关闭当前</div>
      <div class="context-menu-item" @click="closeOtherTabs">关闭其他</div>
      <div class="context-menu-item" @click="closeAllTabs">关闭全部</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useTabsStore } from '@/stores/tabs'

const router = useRouter()
const tabsStore = useTabsStore()
const tabListRef = ref(null)

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  targetTab: null
})

function handleTabClick(tab) {
  tabsStore.setActiveTab(tab.name, router)
}

function handleClose(name) {
  tabsStore.closeTab(name, router)
}

function onWheel(e) {
  if (tabListRef.value) {
    tabListRef.value.scrollLeft += e.deltaY
  }
}

function showContextMenu(e, tab) {
  contextMenu.visible = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.targetTab = tab
}

function hideContextMenu() {
  contextMenu.visible = false
  contextMenu.targetTab = null
}

function closeCurrentTab() {
  if (contextMenu.targetTab?.closable) {
    tabsStore.closeTab(contextMenu.targetTab.name, router)
  }
  hideContextMenu()
}

function closeOtherTabs() {
  const keepName = contextMenu.targetTab?.name || tabsStore.activeTab
  tabsStore.closeOtherTabs(keepName, router)
  hideContextMenu()
}

function closeAllTabs() {
  tabsStore.closeAllTabs(router)
  hideContextMenu()
}

// Click-outside directive (inline)
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => {
      if (!el.contains(e.target)) binding.value(e)
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  }
}
</script>

<style lang="scss" scoped>
.tab-bar {
  height: 40px;
  background: $surface-color;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  position: relative;
  z-index: 9;
}

.tab-list {
  display: flex;
  align-items: center;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  &::-webkit-scrollbar { display: none; }
  padding: 0 8px;
  gap: 2px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: $text-secondary;
  transition: background-color 0.15s, color 0.15s;
  flex-shrink: 0;
  position: relative;

  &:hover {
    background: $background-color;
    color: $text-primary;
  }

  &.is-active {
    color: $primary-color;
    background: rgba(var(--el-color-primary-rgb), 0.08);
    font-weight: 500;

    &::after {
      content: '';
      position: absolute;
      bottom: -4px;
      left: 0;
      right: 0;
      height: 2px;
      background: $primary-color;
      border-radius: 1px;
    }
  }
}

.tab-icon {
  font-size: 14px;
}

.tab-close {
  font-size: 12px;
  border-radius: 50%;
  padding: 1px;
  margin-left: 2px;
  color: $text-secondary;

  &:hover {
    background: rgba(0, 0, 0, 0.1);
    color: $text-primary;
  }
}

.context-menu {
  position: fixed;
  background: $surface-color;
  border: 1px solid $border-color-light;
  border-radius: 6px;
  box-shadow: $box-shadow-md;
  z-index: 9999;
  min-width: 120px;
  padding: 4px 0;
}

.context-menu-item {
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  color: $text-primary;

  &:hover {
    background: $background-color;
    color: $primary-color;
  }
}
</style>
