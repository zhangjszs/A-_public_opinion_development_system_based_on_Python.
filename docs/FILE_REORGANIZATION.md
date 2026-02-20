# 项目文件结构整理变更说明

> 整理日期：2026-02-20

## 一、整理概述

本次整理对项目主目录进行了系统性优化，主要目标包括：
- 建立清晰的子目录结构
- 统一文件命名规范
- 删除冗余和临时文件
- 保留唯一主启动文件

## 二、目录结构变更

### 2.1 新增/调整的目录结构

```
项目根目录/
├── database/          # 数据库脚本（原"数据库/"重命名）
├── data/              # 数据文件集中存放
├── docs/              # 文档集中存放
│   └── plans/         # 计划文档
├── scripts/           # 脚本文件集中存放
├── src/               # 后端源代码
├── frontend/          # 前端源代码
├── tests/             # 测试文件
├── spider_service/    # 爬虫服务
└── .github/           # GitHub配置
```

### 2.2 目录重命名

| 原目录名 | 新目录名 | 说明 |
|---------|---------|------|
| `数据库/` | `database/` | 统一使用英文命名 |

## 三、文件移动记录

### 3.1 文档文件移动（移至 `docs/`）

| 原路径 | 新路径 |
|-------|-------|
| `TODO.md` | `docs/TODO.md` |
| `ARCHITECTURE.md` | `docs/ARCHITECTURE.md` |
| `src/model/MODEL_FIX_SUMMARY.md` | `docs/MODEL_FIX_SUMMARY.md` |
| `.trae/documents/plan_20260209_043118.md` | `docs/plans/plan_20260209_043118.md` |
| `.trae/documents/微博舆情分析系统-全面审查与改进计划.md` | `docs/plans/全面审查与改进计划.md` |

### 3.2 脚本文件移动（移至 `scripts/`）

| 原路径 | 新路径 |
|-------|-------|
| `start.bat` | `scripts/start-all.bat` |
| `frontend/start.bat` | `scripts/start-frontend.bat` |

### 3.3 数据文件移动（移至 `data/`）

| 原路径 | 新路径 |
|-------|-------|
| `src/data/articleData.csv` | `data/articleData.csv` |
| `src/data/commentsData.csv` | `data/commentsData.csv` |
| `src/data/navData.csv` | `data/navData.csv` |
| `src/spider/navData.csv` | `data/spider_navData.csv` |
| `src/spider/userInfo.csv` | `data/spider_userInfo.csv` |

## 四、删除的文件

### 4.1 冗余测试文件

| 文件路径 | 删除原因 |
|---------|---------|
| `src/test_api_new.py` | 临时API测试脚本，功能已被tests/覆盖 |
| `tests/fix_403_error.py` | 临时修复脚本，问题已解决 |
| `tests/fix_403_quick.py` | 临时修复脚本，问题已解决 |
| `tests/test_weibo_minimal.py` | 临时测试脚本 |

### 4.2 演示/示例文件

| 文件路径 | 删除原因 |
|---------|---------|
| `src/spider/demo.py` | 演示脚本，无实际业务用途 |
| `scripts/dem.py` | 演示脚本，无实际业务用途 |

### 4.3 空目录/冗余目录

| 目录路径 | 删除原因 |
|---------|---------|
| `src/data/` | 数据文件已迁移，目录为空 |
| `.trae/documents/` | 文档已迁移，目录为空 |
| `static/` | 根目录冗余静态文件目录（与src/static重复） |

## 五、新增文件

| 文件路径 | 说明 |
|---------|------|
| `start.bat` | 项目主启动脚本（一键启动所有服务） |

## 六、保留在根目录的关键文件

以下文件保留在项目根目录，符合项目规范：

| 文件名 | 用途 |
|-------|------|
| `README.md` | 项目说明文档 |
| `LICENSE.md` | 开源许可证 |
| `run.py` | Python入口文件 |
| `start.bat` | 主启动脚本 |
| `requirements.txt` | Python依赖 |
| `pyproject.toml` | 项目配置 |
| `.gitignore` | Git忽略配置 |
| `.env.example` | 环境变量示例 |

## 七、整理后的目录结构

```
基于python微博舆情分析可视化系统/
├── .github/                    # GitHub配置
│   ├── ISSUE_TEMPLATES/        # Issue模板
│   └── workflows/              # CI/CD工作流
├── .trae/                      # Trae配置
├── database/                   # 数据库脚本
│   ├── article.sql
│   ├── comments.sql
│   ├── database_indexes.sql
│   ├── new.sql
│   └── user.sql
├── data/                       # 数据文件
│   ├── articleData.csv
│   ├── commentsData.csv
│   ├── navData.csv
│   ├── spider_navData.csv
│   └── spider_userInfo.csv
├── docs/                       # 文档
│   ├── plans/                  # 计划文档
│   ├── 演示ppt/                # 演示材料
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CODING_STANDARDS.md
│   ├── CONTRIBUTING.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   ├── MODEL_FIX_SUMMARY.md
│   ├── REVIEW_AND_IMPROVEMENTS.md
│   ├── TODO.md
│   └── 整改执行清单.md
├── frontend/                   # 前端项目
│   ├── public/
│   ├── src/
│   └── ...
├── scripts/                    # 脚本文件
│   ├── check_env.py
│   ├── deploy.py
│   ├── start-all.bat
│   ├── start-frontend.bat
│   └── word_cloud_picture.py
├── spider_service/             # 爬虫服务
├── src/                        # 后端源代码
│   ├── config/
│   ├── model/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── spider/
│   ├── static/
│   ├── tasks/
│   ├── templates/
│   ├── utils/
│   ├── views/
│   ├── app.py
│   └── database.py
├── tests/                      # 测试文件
├── .editorconfig
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE.md
├── README.md
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── requirements.audit.txt
├── run.py
└── start.bat                   # 主启动脚本
```

## 八、使用说明

### 启动项目

```bash
# 方式1：一键启动所有服务（推荐）
start.bat

# 方式2：停止所有服务
start.bat stop

# 方式3：单独启动前端
scripts\start-frontend.bat
```

### 文档查阅

所有项目文档已集中到 `docs/` 目录：
- API文档：`docs/API.md`
- 架构说明：`docs/ARCHITECTURE.md`
- 开发指南：`docs/DEVELOPMENT.md`
- 部署指南：`docs/DEPLOYMENT.md`

## 九、注意事项

1. **代码引用更新**：部分Python文件可能引用了移动的数据文件路径，需要相应更新
2. **Git追踪**：文件移动后Git会自动追踪，无需额外操作
3. **环境变量**：`.env.example` 保留在根目录，实际 `.env` 文件应自行创建

---

*整理完成时间：2026-02-20*
