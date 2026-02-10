# 📚 API 文档

本文档描述本项目后端对外 API 的实际接口与响应规范。

## 📖 概述

### Base URL
- `http://localhost:5000`

### 认证方式
- 需要认证的接口使用 Bearer Token：

```http
Authorization: Bearer <token>
Content-Type: application/json
```

### 统一响应格式

所有 `/api/*`、`/api/spider/*` 与 `/getAllData/*` 接口返回统一结构：

```json
{
  "code": 200,
  "msg": "success",
  "data": {},
  "timestamp": "2026-02-10T12:00:00+00:00",
  "request_id": "9f3d..."
}
```

- `code`：业务码（与 HTTP 状态码保持一致，如 200/400/401/403/404/409/500，异步提交为 202）
- `msg`：提示信息
- `data`：业务数据（可选）
- `timestamp`：UTC 时间戳
- `request_id`：请求追踪 ID（同时也会写入响应头 `X-Request-Id`）

## 🔐 认证（/api/auth）

### 登录
```http
POST /api/auth/login
```

Body:
```json
{ "username": "test", "password": "pass" }
```

返回（成功）：
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "<jwt>",
    "user": { "id": 1, "username": "test", "createTime": "2025-01-01", "is_admin": false }
  },
  "timestamp": "..."
}
```

### 注册
```http
POST /api/auth/register
```

Body:
```json
{ "username": "test", "password": "pass", "confirmPassword": "pass" }
```

### 当前用户
```http
GET /api/auth/me
```

返回：
- `is_admin`: 是否为管理员（用于前端隐藏/保护管理员入口）

### 登出
```http
POST /api/auth/logout
```

## 📊 统计与分析（/api）

### 健康检查
```http
GET /health
```

说明：
- 对外返回最小信息（不包含数据库统计）

### 健康检查（详情，管理员）
```http
GET /api/health/details
```

### 系统概览统计
```http
GET /api/stats/summary
```

### 今日统计
```http
GET /api/stats/today
```

### 文章列表（分页/筛选）
```http
GET /api/articles?page=1&limit=10&keyword=xxx&start_time=2025-01-01&end_time=2025-02-01
```

说明：
- `limit` 最大为 100
- 可选筛选：`type`（文章类型）、`region`（地区，模糊匹配）
- `start_time/end_time` 支持 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`

### 情感分析（支持异步）
```http
POST /api/sentiment/analyze
```

Body:
```json
{ "text": "待分析文本", "mode": "simple", "async": false }
```

异步返回（202）：
```json
{
  "code": 202,
  "msg": "任务已提交",
  "data": { "task_id": "<celery_task_id>", "status": "PENDING", "check_url": "/api/tasks/<id>/status" },
  "timestamp": "..."
}
```

### 查询异步任务状态
```http
GET /api/tasks/<task_id>/status
```

## 🕷️ 爬虫管理（/api 与 /api/spider）

说明：
- 该模块接口需要管理员权限（由 `ADMIN_USERS` 控制）

### 异步：关键词搜索爬虫
```http
POST /api/spider/search
```

Body:
```json
{ "keyword": "关键词", "page_num": 3 }
```

### 异步：评论爬虫
```http
POST /api/spider/comments
```

Body:
```json
{ "article_limit": 50 }
```

### 同步：刷新热门微博（管理员）
```http
POST /api/spider/refresh
```

Body:
```json
{ "page_num": 3 }
```

### 概览（爬虫工作台）
```http
GET /api/spider/overview
```

### 启动后台线程爬取（不依赖 Celery）
```http
POST /api/spider/crawl
```

Body:
```json
{ "type": "hot", "pageNum": 3 }
```

### 状态
```http
GET /api/spider/status
```

### 日志（最近 N 行）
```http
GET /api/spider/logs?lines=200
```

## 🧩 兼容接口（/getAllData）

前端部分分析页面仍使用历史接口（目前也已统一为 `code/msg/data/timestamp`，仅路由前缀不同），例如：
- `GET /getAllData/getHomeData`
- `GET /getAllData/getArticleData`
- `GET /getAllData/getCommentData`
- `GET /getAllData/getIPData`
- `GET /getAllData/getYuqingData`
- `GET /getAllData/getContentCloudData`
- `POST /getAllData/clearCache`
