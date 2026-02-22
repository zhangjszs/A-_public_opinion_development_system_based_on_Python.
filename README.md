# 微博舆情分析可视化系统

基于 Python 的微博舆情分析系统，提供数据采集、情感分析、数据可视化等功能。

## 项目结构

```
基于python微博舆情分析可视化系统/
├── src/                        # 后端源代码
│   ├── app.py                  # Flask 应用入口
│   ├── database.py             # 数据库连接
│   ├── config/                 # 配置文件
│   │   └── settings.py         # 应用配置
│   ├── model/                  # 情感分析模型（训练/推理）
│   │   ├── trainModel.py       # 模型训练
│   │   ├── model_pipeline.py   # 模型流水线
│   │   ├── model_utils.py      # 模型工具函数
│   │   ├── hyperparameter_optimizer.py  # 超参数优化
│   │   ├── data_augmentation.py         # 数据增强
│   │   └── yuqing.py           # 舆情分析入口
│   ├── models/                 # ORM 数据模型
│   │   ├── alert.py            # 预警模型
│   │   ├── article.py          # 文章模型
│   │   ├── comment.py          # 评论模型
│   │   ├── platform.py         # 平台模型
│   │   └── user.py             # 用户模型
│   ├── repositories/           # 数据访问层
│   │   ├── base_repository.py  # 基础仓库
│   │   ├── article_repository.py  # 文章仓库
│   │   ├── comment_repository.py  # 评论仓库
│   │   └── user_repository.py     # 用户仓库
│   ├── services/               # 业务逻辑层
│   │   ├── alert_service.py        # 预警服务
│   │   ├── alert_history_service.py # 预警历史服务
│   │   ├── article_service.py      # 文章服务
│   │   ├── audit_service.py        # 审计服务
│   │   ├── auth_service.py         # 认证服务
│   │   ├── collaboration_service.py # 协作服务
│   │   ├── comment_service.py      # 评论服务
│   │   ├── notification_service.py # 通知服务
│   │   ├── platform_collector.py   # 平台数据采集
│   │   ├── propagation_analyzer.py # 传播分析
│   │   ├── propagation_service.py  # 传播服务
│   │   ├── search_service.py       # 搜索服务
│   │   ├── sentiment_monitor.py    # 情感监控
│   │   ├── sentiment_service.py    # 情感分析服务
│   │   └── websocket_service.py    # WebSocket 服务
│   ├── tasks/                  # 异步任务（Celery）
│   │   ├── celery_config.py    # Celery 配置
│   │   ├── celery_sentiment.py # 情感分析任务
│   │   └── celery_spider.py    # 爬虫任务
│   ├── spider/                 # 微博爬虫模块
│   │   ├── spiderContent.py    # 文章爬虫
│   │   ├── spiderComments.py   # 评论爬虫
│   │   ├── spiderMaster.py     # 爬虫主控
│   │   ├── spiderNav.py        # 导航爬虫
│   │   ├── spiderUserInfo.py   # 用户信息爬虫
│   │   ├── proxy_fetcher.py    # 代理获取
│   │   └── config.py           # 爬虫配置
│   ├── utils/                  # 工具函数
│   │   ├── api_response.py     # 统一响应格式
│   │   ├── authz.py            # 权限校验
│   │   ├── cache.py            # 缓存管理
│   │   ├── chart_renderer.py   # 图表渲染
│   │   ├── constants.py        # 常量定义
│   │   ├── deduplicator.py     # 数据去重
│   │   ├── encryption.py       # 加密工具
│   │   ├── getEchartsData.py   # 图表数据处理
│   │   ├── getHomeData.py      # 首页数据处理
│   │   ├── getTableData.py     # 表格数据处理
│   │   ├── input_validator.py  # 输入校验
│   │   ├── jwt_handler.py      # JWT 处理
│   │   ├── log_sanitizer.py    # 日志脱敏
│   │   ├── pagination.py       # 分页工具
│   │   ├── password_hasher.py  # 密码哈希
│   │   ├── query.py            # 数据库查询
│   │   ├── rate_limiter.py     # 限流工具
│   │   ├── report_generator.py # 报告生成
│   │   ├── sentiment.py        # 情感工具
│   │   └── websocket_server.py # WebSocket 服务端
│   ├── views/                  # 视图/路由
│   │   ├── api/                # REST API 路由
│   │   │   ├── api.py          # 通用 API
│   │   │   ├── alert_api.py    # 预警接口
│   │   │   ├── audit_api.py    # 审计接口
│   │   │   ├── favorites_api.py # 收藏接口
│   │   │   ├── platform_api.py # 平台接口
│   │   │   ├── propagation_api.py # 传播分析接口
│   │   │   ├── report_api.py   # 报告接口
│   │   │   └── spider_api.py   # 爬虫控制接口
│   │   ├── data/               # 数据 API
│   │   │   └── data_api.py     # 数据接口
│   │   ├── page/               # 页面路由
│   │   └── user/               # 用户认证
│   ├── static/                 # 静态资源
│   ├── templates/              # HTML 模板
│   └── cache/                  # 运行时缓存目录
├── frontend/                   # 前端 Vue 项目
│   ├── src/
│   │   ├── api/                # API 接口
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 公共组件
│   │   └── router/             # 路由配置
│   ├── package.json
│   └── vite.config.js
├── docs/                       # 项目文档
├── scripts/                    # 运维脚本
├── tests/                      # 测试用例
├── data/                       # 数据文件目录
├── cache/                      # 缓存目录
├── logs/                       # 日志目录
├── run.py                      # 启动脚本
├── requirements.txt            # Python 依赖
├── requirements-dev.txt        # 开发依赖
├── pyproject.toml              # 工具配置
├── .editorconfig               # 编辑器配置
├── .pre-commit-config.yaml     # Git Hooks
├── .gitignore                  # Git 忽略配置
└── .env.example                # 环境变量示例
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (可选)

### 后端启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 3. 启动后端服务
python run.py
```

后端服务地址: http://127.0.0.1:5000

### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

前端服务地址: http://localhost:3000

## 主要功能

### 数据采集
- 微博文章爬取
- 评论数据采集
- 用户信息获取

### 数据分析
- 情感分析（正面/中性/负面）
- 热词提取
- 地域分布分析
- 时间趋势分析

### 数据可视化
- 首页数据概览
- 热词分析
- 文章分析
- 评论分析
- IP 地域分布
- 舆情趋势
- 词云展示

## API 接口

所有数据接口统一返回格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

### 数据接口列表

| 接口 | 说明 | 缓存时间 |
|------|------|----------|
| `GET /getAllData/getHomeData` | 首页数据 | 5分钟 |
| `GET /getAllData/getTableData` | 表格数据 | 3分钟 |
| `GET /getAllData/getArticleData` | 文章分析 | 10分钟 |
| `GET /getAllData/getCommentData` | 评论分析 | 5分钟 |
| `GET /getAllData/getIPData` | IP 分布 | 10分钟 |
| `GET /getAllData/getYuqingData` | 舆情分析 | 5分钟 |
| `GET /getAllData/getContentCloudData` | 词云数据 | 30分钟 |
| `POST /getAllData/clearCache` | 清空缓存 | - |

## 开发规范

### 代码格式化

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 设置 pre-commit hooks
pre-commit install

# 手动格式化代码
black src/ tests/
isort src/ tests/

# 代码检查
ruff check src/
```

### 项目配置

- **Black**: 代码格式化
- **isort**: import 排序
- **Ruff**: 快速代码检查

详见 [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md)

## 部署

### 生产环境部署

```bash
# 1. 环境检查
python scripts/check_env.py

# 2. 执行部署
python scripts/deploy.py

# 3. 使用 Gunicorn 启动
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.app:app"
```

### Docker 部署 (可选)

```bash
# 构建镜像
docker build -t weibo-analysis .

# 运行容器
docker run -p 5000:5000 weibo-analysis
```

## 目录说明

### 数据目录

- `data/` - 数据文件存储
- `src/data/` - 应用数据文件
- `cache/` - 运行时缓存
- `logs/` - 应用日志

### 缓存策略

- 内存缓存: 使用 `utils/cache.py` 实现
- 缓存时间: 根据数据更新频率设置 3-30 分钟
- 缓存清理: 通过 `/getAllData/clearCache` 接口手动清理

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE.md)

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。
