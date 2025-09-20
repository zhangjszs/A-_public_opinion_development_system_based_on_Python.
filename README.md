# 基于 Python 的微博话题舆情分析管理系统 (Python-based Weibo Public Opinion Analysis System)

## 📖 项目简介 (Project Overview)

本项目是一个基于 Python 技术栈构建的微博话题```
基于python微博舆情分析可视化系统/
├── 📄 README.md                    # 项目说明文档
├── 📄 app.py                       # Flask应用主入口
├── 📄 requirements.txt             # Python依赖包列表
├── 📄 environment.yml              # Conda环境配置
├── 📄 LICENSE.md                   # MIT许可证文件
├── 📄 .gitignore                   # Git忽略文件配置
├── 📁 docs/                        # 项目文档目录
│   ├── 📄 API.md                   # API接口文档
│   ├── 📄 DEPLOYMENT.md            # 部署指南
│   ├── 📄 DEVELOPMENT.md           # 开发指南
│   ├── 📄 CONTRIBUTING.md          # 贡献指南
│   ├── 📄 CHANGELOG.md             # 变更日志
│   ├── 📄 DOCUMENTATION_SUMMARY.md # 文档优化总结
│   └── 📄 配置过程.md               # 中文配置指南
├── 📁 tests/                       # 测试文件目录
│   ├── 📄 test_cookie.py            # Cookie测试脚本
│   ├── 📄 test_db.py                # 数据库测试脚本
│   ├── 📄 test_spider_system.py     # 爬虫系统测试脚本
│   ├── 📄 test_weibo_minimal.py     # 微博最小化测试脚本
│   ├── 📄 check_database.py         # 数据库检查脚本
│   ├── 📄 fix_403_error.py          # 403错误修复脚本
│   └── 📄 fix_403_quick.py          # 快速修复脚本
├── 📁 data/                        # 数据文件目录
│   ├── 📄 articleData.csv           # 文章数据存储
│   └── 📄 navData.csv               # 导航数据存储
├── 📁 scripts/                     # 工具脚本目录
│   ├── 📄 dem.py                    # 数据统计演示脚本
│   └── 📄 word_cloud_picture.py     # 词云图生成脚本
├── 📁 config/                      # 配置文件目录
│   └── 📄 safe_spider_config.txt    # 爬虫安全配置
├── 📁 logs/                        # 日志文件目录
│   ├── 📄 app.log                   # 应用运行日志
│   ├── 📄 model_pipeline.log        # 模型处理日志
│   └── 📄 weibo_spider.log          # 爬虫运行日志
├── 📁 数据库/                      # 数据库相关文件
│   ├── 📄 new.sql                  # 数据库初始化脚本
│   ├── 📄 user.sql                 # 用户表结构
│   ├── 📄 article.sql              # 文章表结构
│   └── 📄 comments.sql             # 评论表结构。旨在通过自动化的数据采集、处理、分析和可视化流程，帮助用户监测特定微博话题的舆情动态、用户情感倾向、热点关键词等，为相关决策提供数据支持。

<!-- 该项目是为参加 **[2025年中国大学生计算机设计大赛 大数据实践赛]** 而开发的作品。 -->

## ✨ 主要功能 (Features)

* **微博数据采集 (Data Collection)**: 定向爬取指定话题相关的微博文章及评论数据。
* **数据清洗与预处理 (Data Cleaning & Preprocessing)**: 对原始数据进行去重、格式化等操作。
* **情感倾向分析 (Sentiment Analysis)**: 利用机器学习模型判断文本的情感极性（积极/消极/中性）。
* **热点分析 (Hotspot Analysis)**: 提取热点词汇，生成词云图。
* **数据可视化 (Data Visualization)**: 通过多种图表（折线图、柱状图、饼图、词云图等）直观展示分析结果。
* **Web 管理界面 (Web Interface)**: 基于 Flask 提供用户友好的浏览器界面进行交互和结果展示。
* **用户管理 (User Management)**: 简单的用户注册与登录功能。

## 🛠️ 技术栈 (Technology Stack)

* **后端 (Backend)**: Python 3.8+, Flask
* **数据处理与分析 (Data Processing & Analysis)**: Pandas, Numpy, Scikit-learn, Jieba
* **数据可视化 (Visualization)**: Matplotlib, Seaborn, WordCloud
* **数据库 (Database)**: MySQL (开发/测试使用 5.7, 部署推荐 8.x+)
* **Web 爬虫 (Web Scraping)**: Requests, BeautifulSoup4, (或 Scrapy/Selenium, 根据实际使用情况填写)
* **模型持久化 (Model Persistence)**: Joblib
* **开发环境管理 (Environment Management)**: Anaconda / venv
* **(开发/调试) (Development/Debugging)**: Flask-DebugToolbar

## 🚀 系统部署与运行 (Deployment and Running)

### 1. 环境准备 (Prerequisites)

* **Git**: 用于获取源代码。
* **Python**: 版本需在 3.8 至 3.12 之间，并确保 `pip` 可用。
* **MySQL**: 安装 MySQL 数据库 (版本 5.7 可用于开发测试，生产环境推荐 8.x+)。
* **(可选) 数据库管理工具**: 如 Navicat, HeidiSQL, MySQL Workbench 等，方便操作。

### 2. 部署步骤 (Deployment Steps)

1.  **获取源代码 (Get Source Code)**
    ```bash
    git clone [https://github.com/](https://github.com/)[你的GitHub用户名]/[你的仓库名称].git
    cd [你的仓库名称]
    ```
    或者下载 ZIP 压缩包并解压。

2.  **数据库初始化 (Initialize Database)**
    * 启动 MySQL 服务。
    * 使用 MySQL 客户端连接数据库。
    * 执行项目 `数据库/` (或其他对应目录) 下的 `new.sql` 脚本，创建 `wb` 数据库及所需的 `article`, `comments`, `user` 表结构。
    * (如果存在) 执行该目录下其他的 `.sql` 文件，导入必要的初始数据或示例数据。

3.  **配置数据库连接 (Configure Database Connection)**
    * 编辑项目代码中的相关配置文件，通常是 `utils/query.py` 和 `spider/main.py` (或根据你的项目结构调整)。
    * 修改其中定义的 MySQL 连接参数 (`host`, `port`, `user`, `password`, `database`='wb')，确保指向步骤 2 中创建并初始化的数据库。

4.  **设置 Python 环境与依赖 (Setup Python Environment & Dependencies)**
    * 在项目根目录下，推荐创建并激活 Python 虚拟环境。
        * 使用 venv:
            ```bash
            python -m venv venv
            # Windows
            .\venv\Scripts\activate
            # macOS/Linux
            source venv/bin/activate
            ```
        * 或使用 Conda:
            ```bash
            # conda create -n weibo_opinion python=3.9 # 创建环境
            conda activate weibo_opinion # 激活环境
            ```
    * 在激活的虚拟环境下，安装所有依赖库：
        ```bash
        pip install -r requirements.txt
        ```

5.  **配置并运行数据爬虫 (Configure & Run Spider - 关键步骤)**
    * **重要**: 运行爬虫前，必须编辑爬虫相关文件 (如 `spider/spiderComments.py`, `spider/spiderContent.py`, `spider/spiderNav.py`)。
    * **更新 Headers**: 将代码中 HTTP 请求头 (`headers`)，特别是 **`'Cookie'`** 和 `'User-Agent'`，**更新为你自己当前浏览器中访问微博时有效的值**。这是成功爬取微博数据的关键，可能需要定期更新。
    * **运行爬虫**: 在激活的虚拟环境下，执行主爬虫脚本开始数据采集：
        ```bash
        python spider/main.py
        ```
    * *此过程可能耗时较长，并可能需要根据微博反爬策略调整代码。*

6.  **(可选) 训练情感分析模型 (Train Sentiment Model)**
    * 如果需要使用 `sentiment_model.py` 训练的模型，请确保标注数据 `target.csv` 存在。
    * ```bash
        python sentiment_model.py
        ```
    * 这将生成 `best_sentiment_model.pkl` 文件。

7.  **启动 Flask Web 应用 (Start Flask Web App)**
    * (推荐) 设置 Flask 环境变量 (在 Linux/macOS):
        ```bash
        export FLASK_APP=app.py  # 或你的主应用文件名
        export FLASK_ENV=development # 开发模式
        ```
        (在 Windows CMD):
        ```cmd
        set FLASK_APP=app.py
        set FLASK_ENV=development
        ```
        (在 Windows PowerShell):
        ```powershell
        $env:FLASK_APP = "app.py"
        $env:FLASK_ENV = "development"
        ```
    * 运行 Flask 开发服务器:
        ```bash
        flask run
        ```
    * 应用默认将在 `http://127.0.0.1:5000` 启动。

### 3. 使用说明 (Usage)

* 在浏览器中访问 `http://127.0.0.1:5000` (或其他 `flask run` 输出的地址)。
* 根据引导完成注册、登录后即可开始使用系统功能。

### 4. 生产环境部署建议 (Production Deployment Considerations)

直接使用 `flask run` 启动的开发服务器不适合用于生产环境。在正式部署时，建议采用更健壮、性能更好的方案：

* **使用 WSGI 服务器**: 如 Gunicorn 或 uWSGI 来运行 Flask 应用。
    * 示例 (Gunicorn): `gunicorn -w 4 -b 0.0.0.0:5000 app:app` ( `-w 4` 表示 4 个工作进程)
* **使用反向代理服务器**: 如 Nginx，部署在 WSGI 服务器之前，负责处理静态文件请求、负载均衡、HTTPS 加密、请求缓冲等。
* **关闭调试模式**: 确保环境变量 `FLASK_ENV` 设置为 `production`。
* **独立部署**: 考虑将数据库、应用服务器部署在不同的物理或虚拟服务器上以提高可用性和安全性。

## 🧠 情感分析模型 (Sentiment Analysis Model)

* 本项目包含一个基于 Scikit-learn 实现的情感分析模块 (`sentiment_model.py`)。
* 采用了 TF-IDF 特征提取和多种分类器（如加权朴素贝叶斯、逻辑回归等）进行训练和比较。
* 通过交叉验证选择模型，并考虑了类别不平衡问题。
* 训练好的模型被保存为 `best_sentiment_model.pkl`，供应用调用。
* **重要提示**: 根据 `target.csv` 数据集和朴素贝叶斯模型的测试结果，当前模型的准确性有待提高，主要受限于数据不平衡。部署前建议优先选择交叉验证中表现更好的模型（如逻辑回归）进行训练评估，或进行数据增强/模型优化。

## 📁 项目结构 (Project Structure)

```
基于python微博舆情分析可视化系统/
├── 📄 README.md                    # 项目说明文档
├── 📄 配置过程.md                   # 部署配置指南
├── 📄 requirements.txt             # Python依赖包列表
├── 📄 environment.yml              # Conda环境配置
├── 📄 .gitignore                   # Git忽略文件配置
├── 🗂️ 数据库/                      # 数据库相关文件
│   ├── 📄 new.sql                  # 数据库初始化脚本
│   ├── 📄 user.sql                 # 用户表结构
│   ├── 📄 article.sql              # 文章表结构
│   └── 📄 comments.sql             # 评论表结构
├── 🗂️ model/                       # 机器学习模型模块
│   ├── 📄 improved_index.py        # 数据预处理模块
│   ├── 📄 improved_yuqing.py       # 情感分析模块
│   ├── 📄 improved_ciPingTotal.py  # 词频分析模块
│   ├── 📄 model_pipeline.py        # 模型处理流水线
│   ├── 📄 model_examples.py        # 模型使用示例
│   ├── 📄 trainModel.py            # 模型训练脚本
│   ├── 📄 MODEL_FIX_SUMMARY.md     # 模型修复总结
│   ├── 📄 best_sentiment_model.pkl # 训练好的情感分析模型
│   ├── 📄 target.csv               # 训练数据集
│   ├── 📄 stopWords.txt            # 停用词列表
│   ├── 📄 comment_1_fenci.txt      # 分词结果文件
│   └── 📄 comment_1_fenci_qutingyongci_cipin.csv # 词频统计结果
├── 🗂️ spider/                      # 网络爬虫模块
│   ├── 📄 main.py                  # 爬虫主程序
│   ├── 📄 config.py                # 爬虫配置管理
│   ├── 📄 improved_config.py       # 改进的爬虫配置
│   ├── 📄 spiderMaster.py          # 爬虫控制器
│   ├── 📄 spiderContent.py         # 文章内容爬取
│   ├── 📄 spiderComments.py        # 评论数据爬取
│   ├── 📄 spiderNav.py             # 导航数据爬取
│   ├── 📄 spiderUserInfo.py        # 用户信息爬取
│   ├── 📄 proxy_fetcher.py         # 代理获取工具
│   ├── 📄 articleData.csv          # 文章数据存储
│   ├── 📄 commentsData.csv         # 评论数据存储
│   ├── 📄 userInfo.csv             # 用户信息存储
│   └── 📄 navData.csv              # 导航数据存储
├── 🗂️ utils/                       # 工具模块
│   ├── 📄 query.py                 # 数据库查询工具
│   ├── 📄 cache.py                 # 缓存管理模块
│   ├── 📄 cache_optimized.py       # 优化缓存系统
│   ├── 📄 getHomeData.py           # 首页数据获取
│   ├── 📄 getPublicData.py         # 公共数据获取
│   ├── 📄 getTableData.py          # 表格数据获取
│   ├── 📄 getEchartsData.py        # 图表数据获取
│   └── 📄 errorResponse.py         # 错误响应处理
├── 🗂️ views/                       # 视图模块
│   ├── 📄 page/                    # 页面视图
│   └── 📄 user/                    # 用户管理视图
├── 🗂️ static/                      # 静态资源
│   ├── 📄 css/                     # 样式文件
│   ├── 📄 js/                      # JavaScript文件
│   ├── 📄 font/                    # 字体文件
│   ├── 📄 image/                   # 图片资源
│   └── 📄 picture/                 # 图片存储
├── 🗂️ templates/                   # HTML模板
│   ├── 📄 404.html                 # 404错误页面
│   ├── 📄 error.html               # 错误页面
│   └── 📄 *.html                   # 其他页面模板
├── 🗂️ cache/                       # 缓存文件目录
├── 🗂️ logs/                        # 日志文件目录
├── 🗂️ 演示ppt/                     # 项目演示文件
├── 📄 app.py                       # Flask应用主入口
├── 📄 dem.py                       # 演示脚本
├── 📄 word_cloud_picture.py        # 词云图生成脚本
└── 📄 *.py                         # 其他Python脚本
```
## 🤝 贡献 (Contributing)

欢迎对本项目提出改进意见或贡献代码！你可以通过以下方式参与：

### 开发流程
1. **Fork 本仓库**
2. **创建你的 Feature 分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **提交你的更改**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **将更改推送到分支**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **打开一个 Pull Request**

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 提交前进行代码格式化

### 问题反馈
- 使用 GitHub Issues 报告问题
- 提供详细的错误信息和复现步骤
- 建议功能时请说明使用场景

### 📚 相关文档
- [详细贡献指南](docs/CONTRIBUTING.md) - 完整的贡献指南和开发规范
- [API 文档](docs/API.md) - 完整的 API 接口文档
- [部署指南](docs/DEPLOYMENT.md) - 详细的部署和生产环境配置
- [开发指南](docs/DEVELOPMENT.md) - 开发者环境设置和开发流程
- [变更日志](docs/CHANGELOG.md) - 项目版本更新历史

## 📄 许可证 (License)

本项目采用 [MIT](LICENSE.md) 许可证。详情请见 `LICENSE.md` 文件。

## 📞 联系方式 (Contact)

- **项目维护者**: [您的姓名]
- **邮箱**: [您的邮箱]
- **GitHub**: [您的GitHub用户名]

## 🙏 致谢 (Acknowledgments)

感谢以下开源项目和工具的支持：
- Flask - Web 框架
- scikit-learn - 机器学习库
- jieba - 中文分词库
- pandas - 数据处理库
- ECharts - 数据可视化库

---

## 🚀 快速开始 (Quick Start)

如果您是首次使用，建议按以下步骤快速启动项目：

```bash
# 1. 克隆项目
git clone https://github.com/zhangjszs/A-_public_opinion_development_system_based_on_Python.git
cd A-_public_opinion_development_system_based_on_Python

# 2. 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库（请先创建MySQL数据库）
# 编辑 utils/query.py 中的数据库连接信息

# 5. 启动应用
python app.py
```

然后在浏览器中访问 `http://127.0.0.1:5000` 即可开始使用！

---

**⭐ 如果这个项目对你有帮助，请给它一个 Star！**
