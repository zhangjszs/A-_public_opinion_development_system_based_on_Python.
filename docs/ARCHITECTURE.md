# 微博舆情分析系统架构演进蓝图 (2025版)

## 1. 现状分析与风险识别

### 1.1 核心问题
*   **高耦合**: `Views` 层承担了 Controller、Service 和 DAO 的所有职责，导致代码难以维护和测试。
*   **贫血模型**: `src/model` 仅用于数据分析，缺乏核心业务领域的实体定义。
*   **同步阻塞**: 大量长耗时任务（如爬虫、NLP分析）直接阻塞 HTTP 请求。
*   **部署脆弱**: 缺乏容器化支持，依赖手动部署，环境一致性差。

### 1.2 风险列表
| 风险项           | 严重等级 | 描述                                      |
| ---------------- | -------- | ----------------------------------------- |
| 接口变更破坏前端 | 高       | 缺乏契约测试，后端改动容易导致前端白屏    |
| 数据库性能瓶颈   | 高       | 缺乏缓存层，复杂查询直接击穿 DB           |
| 扩展性差         | 中       | 无法针对计算密集型任务（NLP）进行独立扩容 |

## 2. 目标架构设计

### 2.1 分层架构 (Layered Architecture)
采用经典的 DDD 分层架构进行重构：
*   **Interfaces (Controller)**: 负责 HTTP 请求解析、参数验证、DTO 转换 (`src/views`)。
*   **Application (Service)**: 负责业务流程编排、事务控制 (`src/services`)。
*   **Domain (Model)**: 负责核心业务逻辑（本次暂未完全实现，建议后续引入）。
*   **Infrastructure (Repository)**: 负责数据持久化、第三方服务调用 (`src/repositories`)。

### 2.2 技术栈升级
*   **Runtime**: Python 3.9 + Flask 2.x
*   **Container**: Docker + Docker Compose
*   **Async**: Celery + Redis (处理爬虫与NLP任务)
*   **CI/CD**: GitHub Actions + Pytest

## 3. 演进路线图 (Milestones)

### Phase 1: 解耦与分层 (已完成)
- [x] 建立 `Repository` 层，封装 SQL 操作。
- [x] 建立 `Service` 层，剥离 `Views` 中的业务逻辑。
- [x] 重构 `Auth` 和 `Article` 相关接口。

### Phase 2: 云原生化 (已完成)
- [x] 添加 `Dockerfile` 和 `docker-compose.yml`。
- [x] 配置 CI/CD 流水线 (`.github/workflows`).

### Phase 3: 深度 DDD 重构 (已完成)
- [x] 统一数据访问层：使用 SQLAlchemy 替换自定义 pymysql 连接池（S10）。
- [x] 定义 `User`、`Article` 等领域实体。
- [ ] 引入 `Domain Event` 解耦业务副作用。

## 6. 数据访问层说明

数据访问层统一使用 SQLAlchemy（`src/utils/query.py`）。`engine`（连接池）和 `db_session`（scoped_session）是唯一的数据库访问入口。`querys()` 和 `query_dataframe()` 提供向后兼容的函数接口，内部均通过 SQLAlchemy engine 执行。

自定义 `DatabasePool`（pymysql）和备用连接机制已于 S10 整改中删除。

### Phase 4: 微服务拆分 (长期目标)
- [ ] 将 `Spider` 模块拆分为独立服务。
- [ ] 将 `NLP Analysis` 拆分为计算密集型服务（Serverless）。

## 4. 性能基准与验收标准
*   **API 延迟**: P99 < 200ms (通过 Redis 缓存实现)。
*   **错误率**: < 0.1%。
*   **测试覆盖率**: 核心业务模块 > 80%。

## 5. 关键代码变更说明
*   `src/repositories/`: 新增数据访问层。
*   `src/services/`: 新增业务逻辑层。
*   `src/views/api/`: 瘦身 Controller，仅保留路由与参数校验。
*   `Dockerfile`: 标准化交付物。
