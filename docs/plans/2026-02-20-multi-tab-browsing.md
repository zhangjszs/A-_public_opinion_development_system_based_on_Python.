# Multi-Tab Browsing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a persistent tab bar between the Header and main content area, wiring up the existing `tabs.js` Pinia store to the UI.

**Architecture:** Insert a new `TabBar.vue` component into `Layout/index.vue` between `<el-header>` and `<el-main>`. The router's `beforeEach` guard calls `tabsStore.addTab(to)` to register tabs automatically. `keep-alive` is bound to `cachedViews` from the store.

**Tech Stack:** Vue 3 Composition API, Pinia (`tabs.js` store already written), Element Plus (icons, dropdown), SCSS

---

### Task 1: Create TabBar.vue component

**Files:**
- Create: `frontend/src/components/Layout/TabBar.vue`

**Step 1: Create the file with template**

```vue
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
```

**Step 2: Add script setup**

```vue
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
```

**Step 3: Add styles**

```vue
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
  scrollbar-width: none; // Firefox
  &::-webkit-scrollbar { display: none; } // Chrome/Safari
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
```

**Step 4: Commit**

```bash
git add frontend/src/components/Layout/TabBar.vue
git commit -m "feat: add TabBar component with scroll and context menu"
```

---

### Task 2: Integrate TabBar into Layout/index.vue

**Files:**
- Modify: `frontend/src/components/Layout/index.vue`

**Step 1: Read the current file**

Read `frontend/src/components/Layout/index.vue` to confirm current structure before editing.

**Step 2: Import TabBar and tabsStore**

In the `<script setup>` block, add:

```javascript
import TabBar from './TabBar.vue'
import { useTabsStore } from '@/stores/tabs'

const tabsStore = useTabsStore()
```

**Step 3: Insert TabBar in template**

Replace:
```html
<el-header class="header" :class="{ 'mobile-header': isMobile }">
  <Header @toggle="toggleSidebar" :is-mobile="isMobile" @toggleMobile="toggleMobileMenu" />
</el-header>
<el-main class="main-content" :class="{ 'mobile-content': isMobile }">
```

With:
```html
<el-header class="header" :class="{ 'mobile-header': isMobile }">
  <Header @toggle="toggleSidebar" :is-mobile="isMobile" @toggleMobile="toggleMobileMenu" />
</el-header>
<TabBar v-if="!isMobile" />
<el-main class="main-content" :class="{ 'mobile-content': isMobile }">
```

**Step 4: Bind keep-alive to cachedViews**

Replace:
```html
<keep-alive>
  <component :is="Component" />
</keep-alive>
```

With:
```html
<keep-alive :include="tabsStore.cachedViews">
  <component :is="Component" />
</keep-alive>
```

**Step 5: Adjust main-content height in styles**

Replace:
```scss
.main-content {
  ...
  height: calc(100vh - 64px);
```

With:
```scss
.main-content {
  ...
  height: calc(100vh - 64px - 40px);
```

**Step 6: Commit**

```bash
git add frontend/src/components/Layout/index.vue
git commit -m "feat: integrate TabBar into layout, bind keep-alive to cachedViews"
```

---

### Task 3: Wire router to tabsStore

**Files:**
- Modify: `frontend/src/router/index.js`

**Step 1: Read the current file**

Read `frontend/src/router/index.js` to confirm the `beforeEach` guard structure.

**Step 2: Import tabsStore in router**

At the top of `router/index.js`, after the existing imports, add:

```javascript
import { useTabsStore } from '@/stores/tabs'
```

**Step 3: Call addTab at end of beforeEach**

In `router.beforeEach`, just before the final `next()` call (the one that runs for authenticated non-admin routes), add the tab registration. The guard currently ends with:

```javascript
  next()
})
```

Replace that final `next()` block with:

```javascript
  // Register tab for authenticated routes
  const tabsStore = useTabsStore()
  tabsStore.addTab(to)
  next()
})
```

Note: `useTabsStore()` must be called inside the guard (after Pinia is initialized), not at module top level.

**Step 4: Verify home tab is not duplicated**

The `addTab` method in `tabs.js` already checks for existing tabs by `name` and skips duplicates — no extra logic needed.

**Step 5: Commit**

```bash
git add frontend/src/router/index.js
git commit -m "feat: auto-register tabs on route navigation"
```

---

### Task 4: Manual smoke test

**Step 1: Start the dev server**

Run in terminal (do NOT run via Claude):
```bash
cd frontend && npm run dev
```

**Step 2: Verify tab behavior**

1. Log in → Home tab appears, not closable
2. Navigate to "热词统计" → new tab appears, becomes active
3. Navigate to "文章分析" → another tab appears
4. Click Home tab → navigates back, Home tab active
5. Click × on "热词统计" → tab closes, adjacent tab activates
6. Right-click a tab → context menu appears with 3 options
7. "关闭其他" → only right-clicked tab remains
8. "关闭全部" → only Home tab remains, navigates to /home
9. Open many tabs until overflow → horizontal scroll works with mouse wheel
10. Refresh page → tabs restored from localStorage

**Step 3: Verify keep-alive**

1. Open "首页" and scroll down
2. Navigate to another tab
3. Navigate back to "首页" → scroll position preserved (keep-alive working)

**Step 4: Final commit if any fixes were needed**

```bash
git add -p
git commit -m "fix: tab bar smoke test fixes"
```
