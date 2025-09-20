# 📚 API 文档 (API Documentation)

本文档详细介绍微博舆情分析系统的 API 接口规范。

## 📋 目录

- [概述](#概述)
- [认证](#认证)
- [数据接口](#数据接口)
- [用户管理](#用户管理)
- [错误处理](#错误处理)
- [示例代码](#示例代码)

## 📖 概述

### 基础信息
- **Base URL**: `http://localhost:5000`
- **API 版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8

### 请求格式
```http
Content-Type: application/json
Authorization: Bearer <token>  # 如果需要认证
```

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": "2025-09-20T10:00:00Z"
}
```

## 🔐 认证

### 用户登录
```http
POST /user/login
```

**请求体**:
```json
{
    "username": "string",
    "password": "string"
}
```

**响应**:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "user_id": 1,
        "username": "testuser",
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "expires_in": 3600
    }
}
```

### 用户注册
```http
POST /user/register
```

**请求体**:
```json
{
    "username": "string",
    "password": "string",
    "email": "string"
}
```

### 用户登出
```http
POST /user/logout
```

## 📊 数据接口

### 获取首页数据
```http
GET /api/home
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "total_articles": 1250,
        "total_comments": 5600,
        "sentiment_distribution": {
            "positive": 45.2,
            "negative": 23.1,
            "neutral": 31.7
        },
        "hot_topics": [
            {"topic": "科技", "count": 234},
            {"topic": "娱乐", "count": 189}
        ]
    }
}
```

### 获取文章列表
```http
GET /api/articles
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20)
- `keyword`: 关键词搜索
- `sentiment`: 情感过滤 (positive/negative/neutral)
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应**:
```json
{
    "code": 200,
    "data": {
        "articles": [
            {
                "id": 1,
                "title": "文章标题",
                "content": "文章内容...",
                "author": "作者名",
                "created_at": "2025-09-20T08:00:00Z",
                "sentiment": "positive",
                "likes": 125,
                "comments": 23,
                "reposts": 5
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 1250,
            "pages": 63
        }
    }
}
```

### 获取文章详情
```http
GET /api/articles/{article_id}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "title": "文章标题",
        "content": "完整文章内容...",
        "author": "作者名",
        "created_at": "2025-09-20T08:00:00Z",
        "sentiment": "positive",
        "sentiment_score": 0.85,
        "likes": 125,
        "comments": 23,
        "reposts": 5,
        "region": "北京",
        "tags": ["科技", "AI", "创新"]
    }
}
```

### 获取评论数据
```http
GET /api/comments
```

**查询参数**:
- `article_id`: 文章ID
- `page`: 页码
- `per_page`: 每页数量
- `sentiment`: 情感过滤

**响应**:
```json
{
    "code": 200,
    "data": {
        "comments": [
            {
                "id": 1,
                "article_id": 1,
                "content": "评论内容...",
                "author": "评论者",
                "created_at": "2025-09-20T09:00:00Z",
                "sentiment": "positive",
                "likes": 12,
                "replies": 3
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 5600,
            "pages": 280
        }
    }
}
```

### 获取情感分析统计
```http
GET /api/sentiment/stats
```

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `group_by`: 分组方式 (hour/day/week/month)

**响应**:
```json
{
    "code": 200,
    "data": {
        "total": 5600,
        "distribution": {
            "positive": 45.2,
            "negative": 23.1,
            "neutral": 31.7
        },
        "trend": [
            {"date": "2025-09-20", "positive": 120, "negative": 45, "neutral": 78},
            {"date": "2025-09-19", "positive": 98, "negative": 67, "neutral": 89}
        ]
    }
}
```

### 获取词频分析
```http
GET /api/words/frequency
```

**查询参数**:
- `limit`: 返回数量 (默认: 50)
- `min_freq`: 最小频率 (默认: 5)

**响应**:
```json
{
    "code": 200,
    "data": {
        "words": [
            {"word": "中国", "frequency": 234, "sentiment": "neutral"},
            {"word": "发展", "frequency": 189, "sentiment": "positive"},
            {"word": "经济", "frequency": 156, "sentiment": "positive"}
        ],
        "total_words": 12500,
        "unique_words": 3456
    }
}
```

### 获取图表数据
```http
GET /api/charts/{chart_type}
```

**支持的图表类型**:
- `sentiment_pie`: 情感分布饼图
- `trend_line`: 情感趋势折线图
- `word_cloud`: 词云图
- `region_map`: 地域分布地图
- `hot_topics`: 热门话题柱状图

**响应**:
```json
{
    "code": 200,
    "data": {
        "chart_type": "sentiment_pie",
        "title": "情感分布统计",
        "data": [
            {"name": "积极", "value": 45.2, "color": "#52c41a"},
            {"name": "消极", "value": 23.1, "color": "#ff4d4f"},
            {"name": "中性", "value": 31.7, "color": "#1890ff"}
        ]
    }
}
```

## 👤 用户管理

### 获取用户信息
```http
GET /api/user/profile
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "user_id": 1,
        "username": "testuser",
        "email": "user@example.com",
        "created_at": "2025-09-15T10:00:00Z",
        "last_login": "2025-09-20T09:00:00Z",
        "role": "user"
    }
}
```

### 更新用户信息
```http
PUT /api/user/profile
```

**请求体**:
```json
{
    "email": "newemail@example.com",
    "nickname": "新昵称"
}
```

### 修改密码
```http
PUT /api/user/password
```

**请求体**:
```json
{
    "old_password": "oldpassword",
    "new_password": "newpassword"
}
```

## ⚠️ 错误处理

### 错误响应格式
```json
{
    "code": 400,
    "message": "参数错误",
    "error": "详细错误信息",
    "timestamp": "2025-09-20T10:00:00Z"
}
```

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权 | 重新登录 |
| 403 | 权限不足 | 联系管理员 |
| 404 | 资源不存在 | 检查URL和参数 |
| 429 | 请求过于频繁 | 稍后重试 |
| 500 | 服务器内部错误 | 联系技术支持 |

### 错误示例
```json
{
    "code": 400,
    "message": "参数验证失败",
    "error": "用户名不能为空",
    "timestamp": "2025-09-20T10:00:00Z"
}
```

## 💻 示例代码

### Python 客户端示例

```python
import requests
import json

class WeiboAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        """用户登录"""
        response = self.session.post(f"{self.base_url}/user/login", json={
            "username": username,
            "password": password
        })
        data = response.json()
        if data['code'] == 200:
            self.token = data['data']['token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
        return data

    def get_articles(self, page=1, per_page=20, **filters):
        """获取文章列表"""
        params = {'page': page, 'per_page': per_page, **filters}
        response = self.session.get(f"{self.base_url}/api/articles", params=params)
        return response.json()

    def get_sentiment_stats(self, **params):
        """获取情感统计"""
        response = self.session.get(f"{self.base_url}/api/sentiment/stats", params=params)
        return response.json()

    def get_word_frequency(self, limit=50):
        """获取词频统计"""
        response = self.session.get(f"{self.base_url}/api/words/frequency",
                                  params={'limit': limit})
        return response.json()

# 使用示例
client = WeiboAPIClient()
client.login("username", "password")

# 获取文章
articles = client.get_articles(page=1, sentiment="positive")
print(f"获取到 {len(articles['data']['articles'])} 篇文章")

# 获取情感统计
stats = client.get_sentiment_stats()
print(f"积极情感占比: {stats['data']['distribution']['positive']}%")
```

### JavaScript 客户端示例

```javascript
class WeiboAPIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        const response = await fetch(url, config);
        return response.json();
    }

    async login(username, password) {
        const data = await this.request('/user/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (data.code === 200) {
            this.token = data.data.token;
            localStorage.setItem('token', this.token);
        }

        return data;
    }

    async getArticles(params = {}) {
        return this.request('/api/articles', { params });
    }

    async getSentimentStats(params = {}) {
        return this.request('/api/sentiment/stats', { params });
    }

    async getWordFrequency(limit = 50) {
        return this.request('/api/words/frequency', {
            params: { limit }
        });
    }
}

// 使用示例
const client = new WeiboAPIClient();

// 登录
await client.login('username', 'password');

// 获取数据
const articles = await client.getArticles({ page: 1, sentiment: 'positive' });
const stats = await client.getSentimentStats();
const words = await client.getWordFrequency(20);
```

### cURL 示例

```bash
# 登录
curl -X POST http://localhost:5000/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 获取文章列表
curl -X GET "http://localhost:5000/api/articles?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取情感统计
curl -X GET "http://localhost:5000/api/sentiment/stats?start_date=2025-09-01&end_date=2025-09-20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取词频统计
curl -X GET "http://localhost:5000/api/words/frequency?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔄 版本历史

### v1.0 (2025-09-20)
- 初始版本发布
- 支持基础的文章、评论、情感分析接口
- 提供用户认证功能
- 支持数据可视化图表接口

---

**最后更新**: 2025年9月20日