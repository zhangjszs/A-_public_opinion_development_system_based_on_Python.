# 用户体验三功能设计文档

日期：2026-02-20

## 功能一：收藏/书签

### 现状
代码全部已写好，未提交：
- `src/views/api/favorites_api.py` — 5 个 API 端点，已在 app.py 注册
- `frontend/src/api/favorites.js` — 前端 API 客户端
- `frontend/src/views/user/Favorites.vue` — 收藏列表页
- `frontend/src/views/analysis/article.vue` — 已有收藏星标按钮
- `frontend/src/api/user.js` — 用户 API 客户端
- `frontend/src/views/user/Profile.vue` — 个人中心页

### 需要做的
1. git add 并 commit 所有未提交文件
2. 验证后端路由注册正确（favorites_bp 已在 app.py 注册）

---

## 功能二：帮助文档

### 现状
`frontend/src/views/system/Help.vue` 已写好，包含：
- 8 个功能介绍卡片
- 6 条 FAQ
- 5 步快速入门
- 系统信息（版本、技术栈）

路由已在 router/index.js 注册：`/help` → `Help`

### 需要做的
1. git add 并 commit Help.vue

---

## 功能三：仪表盘自定义布局

### 现状
`frontend/src/views/home/index.vue` 已有：
- widgets 数组（含 visible 属性）
- 设置抽屉（显隐开关）
- localStorage 持久化

### 新增内容

**依赖**：安装 `vue-draggable-plus`

**Widget 数据结构扩展**：
```javascript
// 每个 widget 增加 span 属性
{ id: 'stats', title: '统计卡片', visible: true, span: 24 }
// span: 12 = 半宽(el-col :span="12"), 24 = 全宽
```

**设置抽屉改造**：
- widget 列表用 `<VueDraggable>` 包裹，支持拖拽排序
- 每个 widget 行右侧加宽度切换按钮（半宽/全宽图标）
- 拖拽手柄图标（DragHandle）

**主页面布局**：
- `el-col` 的 `:span` 绑定 `widget.span`
- 顺序由 widgets 数组顺序决定

**持久化**：widgets 数组（含 span 和顺序）存 localStorage

---

## 文件变更清单

| 文件 | 操作 |
|------|------|
| `src/views/api/favorites_api.py` | 提交（已有） |
| `frontend/src/api/favorites.js` | 提交（已有） |
| `frontend/src/api/user.js` | 提交（已有） |
| `frontend/src/views/user/Favorites.vue` | 提交（已有） |
| `frontend/src/views/user/Profile.vue` | 提交（已有） |
| `frontend/src/views/system/Help.vue` | 提交（已有） |
| `frontend/src/views/home/index.vue` | 修改（拖拽 + span） |
| `frontend/package.json` | 修改（添加 vue-draggable-plus） |
