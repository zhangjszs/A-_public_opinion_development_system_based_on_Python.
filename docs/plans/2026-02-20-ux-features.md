# 用户体验三功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 完成收藏/书签、帮助文档、仪表盘自定义布局（拖拽排序+大小调整）三个功能。

**Architecture:** 收藏和帮助文档的代码已全部写好，只需提交未跟踪文件。仪表盘需要安装 vue-draggable-plus，将现有 widgets 数组改造为支持拖拽排序和 span 大小的结构，并更新设置抽屉 UI。

**Tech Stack:** Vue 3 Composition API, Pinia, Element Plus, vue-draggable-plus, SCSS

---

### Task 1: 提交收藏功能和帮助文档的已有文件

**Files:**
- Commit: `src/views/api/favorites_api.py`
- Commit: `src/services/audit_service.py`
- Commit: `src/utils/encryption.py`
- Commit: `src/views/api/audit_api.py`
- Commit: `frontend/src/api/favorites.js`
- Commit: `frontend/src/api/user.js`
- Commit: `frontend/src/views/user/Favorites.vue`
- Commit: `frontend/src/views/user/Profile.vue`
- Commit: `frontend/src/views/system/Help.vue`
- Commit: `frontend/src/directives/` (directory)
- Commit: `run_migration.py`
- Commit: `docs/migrations/`

**Step 1: Check git status**

```bash
git status
```

Expected: See all the untracked files listed above.

**Step 2: Stage and commit all existing feature files**

```bash
git add src/views/api/favorites_api.py src/services/audit_service.py src/utils/encryption.py src/views/api/audit_api.py
git add frontend/src/api/favorites.js frontend/src/api/user.js
git add frontend/src/views/user/Favorites.vue frontend/src/views/user/Profile.vue
git add frontend/src/views/system/Help.vue
git add frontend/src/directives/ frontend/src/stores/tabs.js
git add run_migration.py docs/migrations/
git commit -m "feat: add favorites, user profile, help center, audit features"
```

**Step 3: Verify commit**

```bash
git log --oneline -3
```

Expected: New commit at top.

---

### Task 2: 安装 vue-draggable-plus

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install the package**

Run in `frontend/` directory:
```bash
npm install vue-draggable-plus
```

**Step 2: Verify installation**

```bash
cat frontend/package.json | grep vue-draggable-plus
```

Expected: `"vue-draggable-plus": "^x.x.x"` in dependencies.

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: install vue-draggable-plus for dashboard drag-and-drop"
```

---

### Task 3: 改造仪表盘 home/index.vue — 数据结构

**Files:**
- Modify: `frontend/src/views/home/index.vue`

**Step 1: Read the current file**

Read `frontend/src/views/home/index.vue` lines 136-180 (script setup, widget section).

**Step 2: Replace widget data structure**

Find and replace the current widget section in `<script setup>`:

Old code:
```javascript
// Dashboard customization
const showSettings = ref(false)
const defaultWidgets = { stats: true, timeline: true, charts: true }
const widgetOptions = [
  { key: 'stats', label: '统计卡片（文章数/今日新增/最火作者/热门地区）' },
  { key: 'timeline', label: '文章发布时间分布' },
  { key: 'charts', label: '评论Top5 / 类型占比 / 时间占比' },
]

const loadWidgets = () => {
  try {
    const saved = localStorage.getItem('dashboard_widgets')
    return saved ? { ...defaultWidgets, ...JSON.parse(saved) } : { ...defaultWidgets }
  } catch { return { ...defaultWidgets } }
}
const widgets = reactive(loadWidgets())
const saveWidgets = () => localStorage.setItem('dashboard_widgets', JSON.stringify(widgets))
const resetWidgets = () => { Object.assign(widgets, defaultWidgets); saveWidgets() }
```

New code:
```javascript
// Dashboard customization
const showSettings = ref(false)

const defaultWidgetList = [
  { key: 'stats',    label: '统计卡片',       visible: true, span: 24 },
  { key: 'timeline', label: '文章发布时间分布', visible: true, span: 24 },
  { key: 'charts',   label: '图表区（评论/类型/时间）', visible: true, span: 24 },
]

const loadWidgetList = () => {
  try {
    const saved = localStorage.getItem('dashboard_widget_list')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length === defaultWidgetList.length) {
        return parsed
      }
    }
  } catch { /* ignore */ }
  return defaultWidgetList.map(w => ({ ...w }))
}

const widgetList = ref(loadWidgetList())
const saveWidgetList = () => localStorage.setItem('dashboard_widget_list', JSON.stringify(widgetList.value))
const resetWidgets = () => {
  widgetList.value = defaultWidgetList.map(w => ({ ...w }))
  saveWidgetList()
}
```

**Step 3: Update import line**

Find:
```javascript
import { ref, onMounted, computed, reactive } from 'vue'
```

Replace with:
```javascript
import { ref, onMounted, computed } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
```

---

### Task 4: 改造仪表盘 home/index.vue — 模板

**Files:**
- Modify: `frontend/src/views/home/index.vue`

**Step 1: Replace template widget rendering**

The current template has three separate `v-if="widgets.xxx"` blocks. Replace the entire template content (lines 1-133) with the new draggable-aware version:

```html
<template>
  <div class="home-container">
    <div class="dashboard-toolbar">
      <el-button :icon="Setting" circle size="small" @click="showSettings = true" title="自定义布局" />
    </div>

    <template v-for="widget in widgetList" :key="widget.key">
      <!-- 统计卡片 -->
      <el-row v-if="widget.key === 'stats' && widget.visible" :gutter="24" class="stat-row">
        <el-col :xs="24" :sm="12" :md="6">
          <StatCard :value="statsData.articleCount" label="总文章数" icon="Document" bg-color="#EFF6FF" icon-color="#2563EB" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <StatCard :value="statsData.todayCount" label="今日新增" icon="TrendCharts" bg-color="#ECFDF5" icon-color="#059669" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <StatCard :value="statsData.topAuthor" label="最火作者" icon="User" bg-color="#FFFBEB" icon-color="#D97706" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <StatCard :value="statsData.topRegion" label="热门地区" icon="Location" bg-color="#FFF1F2" icon-color="#E11D48" />
        </el-col>
      </el-row>

      <!-- 时间线图表 -->
      <el-row v-if="widget.key === 'timeline' && widget.visible" :gutter="24" class="mb-4">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span class="header-title">文章发布时间分布</span>
                <el-button type="primary" plain size="small" :icon="Refresh" @click="refreshData">刷新数据</el-button>
              </div>
            </template>
            <BaseChart ref="lineChartRef" :options="lineChartOptions" height="350px" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区 -->
      <el-row v-if="widget.key === 'charts' && widget.visible" :gutter="24">
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card">
            <template #header><span class="header-title">评论点赞量 Top 5</span></template>
            <div class="top-comments">
              <div v-for="(comment, index) in topComments" :key="index" class="comment-item">
                <div class="comment-avatar">{{ comment.user.charAt(0) }}</div>
                <div class="comment-info">
                  <div class="comment-header">
                    <span class="comment-user">{{ comment.user }}</span>
                    <span class="comment-likes"><el-icon><StarFilled /></el-icon> {{ comment.likes }}</span>
                  </div>
                  <div class="comment-content" :title="comment.content">{{ comment.content }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card">
            <template #header><span class="header-title">文章类型占比</span></template>
            <BaseChart ref="pieChartRef" :options="pieChartOptions" height="350px" />
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card">
            <template #header><span class="header-title">评论用户时间占比</span></template>
            <BaseChart ref="timePieChartRef" :options="timePieChartOptions" height="350px" />
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- 自定义布局抽屉 -->
    <el-drawer v-model="showSettings" title="仪表盘布局设置" size="320px" :append-to-body="true">
      <div class="widget-settings">
        <p class="settings-tip">拖拽调整顺序，切换显示/隐藏，选择宽度</p>
        <VueDraggable v-model="widgetList" handle=".drag-handle" @end="saveWidgetList">
          <div class="widget-item" v-for="opt in widgetList" :key="opt.key">
            <el-icon class="drag-handle"><Rank /></el-icon>
            <el-switch v-model="opt.visible" @change="saveWidgetList" />
            <span class="widget-label">{{ opt.label }}</span>
            <el-tooltip :content="opt.span === 24 ? '切换为半宽' : '切换为全宽'" placement="top">
              <el-button
                :icon="opt.span === 24 ? 'Grid' : 'FullScreen'"
                circle
                size="small"
                class="span-btn"
                @click="toggleSpan(opt)"
              />
            </el-tooltip>
          </div>
        </VueDraggable>
        <el-divider />
        <el-button type="primary" plain size="small" @click="resetWidgets">恢复默认布局</el-button>
      </div>
    </el-drawer>
  </div>
</template>
```

**Step 2: Add toggleSpan function to script**

After `resetWidgets`, add:
```javascript
const toggleSpan = (widget) => {
  widget.span = widget.span === 24 ? 12 : 24
  saveWidgetList()
}
```

**Step 3: Add Rank icon to imports**

Find:
```javascript
import { Refresh, StarFilled, Setting } from '@element-plus/icons-vue'
```

Replace with:
```javascript
import { Refresh, StarFilled, Setting, Rank } from '@element-plus/icons-vue'
```

---

### Task 5: 更新仪表盘 SCSS 样式

**Files:**
- Modify: `frontend/src/views/home/index.vue` (style section)

**Step 1: Update widget-item styles**

Find in `<style lang="scss" scoped>`:
```scss
    .widget-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid $border-color-light;

      .widget-label {
        font-size: 13px;
        color: $text-primary;
      }
    }
```

Replace with:
```scss
    .widget-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 0;
      border-bottom: 1px solid $border-color-light;
      cursor: default;

      .drag-handle {
        cursor: grab;
        color: $text-secondary;
        font-size: 16px;
        flex-shrink: 0;
        &:active { cursor: grabbing; }
      }

      .widget-label {
        font-size: 13px;
        color: $text-primary;
        flex: 1;
      }

      .span-btn {
        flex-shrink: 0;
      }
    }
```

**Step 2: Commit all home/index.vue changes**

```bash
git add frontend/src/views/home/index.vue
git commit -m "feat: dashboard drag-and-drop reorder and span toggle"
```

---

### Task 6: 手动验证

**Step 1: Start dev server (run manually)**

```bash
cd frontend && npm run dev
```

**Step 2: Verify favorites**

1. 登录后访问 `/article-analysis`
2. 文章列表中每行应有星标图标
3. 点击星标 → 变为实心，再点 → 取消收藏
4. 访问 `/favorites` → 显示已收藏文章列表

**Step 3: Verify help center**

1. 访问 `/help`
2. 应显示功能介绍、FAQ、快速入门、系统信息四个区块

**Step 4: Verify dashboard customization**

1. 访问 `/home`
2. 点击右上角设置图标 → 抽屉打开
3. 拖拽 widget 行 → 顺序改变，主页面顺序同步更新
4. 点击宽度切换按钮 → widget 在全宽/半宽间切换（注意：stats 和 charts 是 el-row，span 对它们的效果体现在外层 el-col 上，timeline 是全宽 el-col）
5. 关闭开关 → widget 隐藏
6. 刷新页面 → 设置保留

**Step 5: Final commit if fixes needed**

```bash
git add -p
git commit -m "fix: dashboard/favorites/help smoke test fixes"
```
