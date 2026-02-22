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

## 🔔 预警管理（/api/alert）

### 获取预警规则列表
```http
GET /api/alert/rules
```

### 创建预警规则
```http
POST /api/alert/rules
```

Body:
```json
{
  "id": "custom_rule_1",
  "name": "自定义预警规则",
  "alert_type": "custom",
  "level": "warning",
  "conditions": {},
  "cooldown_minutes": 30
}
```

### 更新预警规则
```http
PUT /api/alert/rules/<id>
```

Body:
```json
{
  "name": "更新后的规则名",
  "enabled": true,
  "conditions": {},
  "cooldown_minutes": 30,
  "level": "warning"
}
```

### 删除预警规则
```http
DELETE /api/alert/rules/<id>
```

### 切换预警规则启用状态
```http
POST /api/alert/rules/<id>/toggle
```

### 获取预警历史
```http
GET /api/alert/history?limit=50&level=warning&unread_only=false
```

参数：
- `limit`: 返回数量（默认50，最大200）
- `level`: 按级别筛选（可选）
- `unread_only`: 仅返回未读（默认false）

### 获取预警统计
```http
GET /api/alert/stats
```

### 获取未读预警数量
```http
GET /api/alert/unread-count
```

### 标记预警已读
```http
POST /api/alert/<id>/read
```

### 标记所有预警已读
```http
POST /api/alert/read-all
```

### 测试预警功能
```http
POST /api/alert/test
```

Body:
```json
{
  "type": "info",
  "message": "这是一条测试预警"
}
```

### 评估数据触发预警
```http
POST /api/alert/evaluate
```

Body:
```json
{
  "type": "volume_spike",
  "current_count": 100,
  "baseline_count": 20,
  "time_window": 60
}
```

## 📄 报告生成（/api/report）

### 生成报告
```http
POST /api/report/generate
```

Body:
```json
{
  "format": "pdf",
  "title": "舆情分析报告",
  "template": "standard",
  "sections": ["summary", "sentiment", "topics"],
  "data": {}
}
```

### 生成所有格式报告
```http
POST /api/report/generate-all
```

Body:
```json
{
  "title": "舆情分析报告",
  "data": {}
}
```

### 下载报告文件
```http
GET /api/report/download/<filename>
```

### 预览报告文件
```http
GET /api/report/preview/<filename>
```

### 获取报告模板列表
```http
GET /api/report/templates
```

### 获取演示数据
```http
GET /api/report/demo-data
```

## 🌐 传播路径分析（/api/propagation）

### 分析文章传播路径
```http
GET /api/propagation/analyze/<article_id>?demo=true&count=100
```

参数：
- `demo`: 使用演示数据（默认true）
- `count`: 节点数量（默认100）

### 获取传播图数据
```http
GET /api/propagation/graph/<article_id>?demo=true&count=80
```

### 获取KOL影响力分析
```http
GET /api/propagation/kol/<article_id>?demo=true
```

### 获取传播时间线
```http
GET /api/propagation/timeline/<article_id>?interval=60
```

参数：
- `interval`: 时间间隔（分钟，默认60）

### 获取传播深度分布
```http
GET /api/propagation/depth/<article_id>
```

### 对比多条传播路径
```http
POST /api/propagation/compare
```

Body:
```json
{
  "article_ids": ["article_1", "article_2", "article_3"]
}
```

## 🖥️ 多平台数据（/api/platform）

### 获取平台列表
```http
GET /api/platform/list
```

### 获取指定平台数据
```http
GET /api/platform/data/<platform>?page=1&page_size=20&demo=true
```

参数：
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）
- `demo`: 使用演示数据（默认true）

### 获取所有平台汇总数据
```http
GET /api/platform/all?platforms=weibo,wechat,douyin,zhihu&page_size=10
```

### 获取平台统计数据
```http
GET /api/platform/stats/<platform>
```

说明：
- `<platform>` 可以是具体平台ID或 `all`

### 对比多个平台数据
```http
POST /api/platform/compare
```

Body:
```json
{
  "platforms": ["weibo", "wechat", "douyin"]
}
```
