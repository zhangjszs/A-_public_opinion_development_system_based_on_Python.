# 多标签页浏览设计文档

日期：2026-02-20

## 需求

在后台管理布局中实现类 VS Code 风格的多标签页浏览，支持：
- 关闭单个标签（首页不可关闭）
- 右键菜单（关闭当前、关闭其他、关闭全部）
- 标签溢出横向滚动
- keep-alive 组件缓存

## 布局结构

```
el-container
  ├── el-aside (Sidebar)
  └── el-container
        ├── el-header (Header - 64px)
        ├── TabBar (新增 - 40px)
        └── el-main (内容区)
```

## 组件设计

### TabBar.vue（新建）

位置：`frontend/src/components/Layout/TabBar.vue`

功能：
- 读取 `useTabsStore()` 的 `tabs`、`activeTab`
- 标签列表横向排列，`overflow-x: auto`，隐藏原生滚动条
- 鼠标滚轮事件转换为横向滚动
- 每个标签：图标 + 标题 + × 按钮（`closable: false` 的标签无 ×）
- 激活标签：底部蓝色 2px 边框高亮
- 右键菜单：`el-dropdown` contextmenu 触发，选项：关闭当前 / 关闭其他 / 关闭全部

### Layout/index.vue（修改）

1. 引入并插入 `<TabBar />` 在 Header 和 main 之间
2. `main-content` 高度从 `calc(100vh - 64px)` 改为 `calc(100vh - 64px - 40px)`
3. `<keep-alive :include="cachedViews">` 绑定 tabs store

### router/index.js（修改）

在 `beforeEach` 守卫末尾，对非 public 路由调用 `tabsStore.addTab(to)`。

## 数据流

```
路由跳转 → beforeEach → tabsStore.addTab(to)
                              ↓
                        tabs[] 更新 → TabBar 重渲染
                              ↓
                        cachedViews 更新 → keep-alive 缓存
```

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `frontend/src/components/Layout/TabBar.vue` | 新建 |
| `frontend/src/components/Layout/index.vue` | 修改 |
| `frontend/src/router/index.js` | 修改 |
