# 🚀 部署指南 (Deployment Guide)

本文档提供完整的项目部署和运行指南，包括开发环境和生产环境的部署方法。

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [数据库配置](#数据库配置)
- [依赖安装](#依赖安装)
- [爬虫配置](#爬虫配置)
- [应用启动](#应用启动)
- [生产部署](#生产部署)
- [故障排除](#故障排除)

## ⚡ 快速开始

### 使用脚本一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/zhangjszs/A-_public_opinion_development_system_based_on_Python.git
cd A-_public_opinion_development_system_based_on_Python

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 手动部署

```bash
# 1. 环境准备
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库初始化
mysql -u root -p < 数据库/new.sql

# 4. 配置数据库连接
# 编辑 utils/query.py 中的连接信息

# 5. 启动应用
python app.py
```

## 🔧 环境要求

### 系统要求
- **操作系统**: Windows 10+ / Ubuntu 18.04+ / macOS 10.15+
- **内存**: 至少 4GB RAM
- **磁盘**: 至少 2GB 可用空间

### 软件要求
- **Python**: 3.8 - 3.12
- **MySQL**: 5.7+ (推荐 8.0+)
- **Git**: 2.0+
- **Node.js**: 14+ (可选，用于前端构建)

### Python 依赖包
主要依赖包已在 `requirements.txt` 中列出：
```
Flask==3.1.0
pandas==2.2.3
scikit-learn==1.6.1
jieba==0.42.1
PyMySQL==1.1.1
matplotlib==3.9.2
wordcloud==1.9.3
```

## 🗄️ 数据库配置

### 1. MySQL 安装

#### Windows
```bash
# 使用 Chocolatey 安装
choco install mysql

# 或下载 MSI 安装包
# https://dev.mysql.com/downloads/mysql/
```

#### Ubuntu
```bash
sudo apt update
sudo apt install mysql-server-8.0
sudo mysql_secure_installation
```

#### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### 2. 数据库初始化

```bash
# 连接到 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE wb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构
USE wb;
SOURCE 数据库/new.sql;
SOURCE 数据库/user.sql;
SOURCE 数据库/article.sql;
SOURCE 数据库/comments.sql;

# 创建用户（可选）
CREATE USER 'weibo_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON wb.* TO 'weibo_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 配置文件修改

编辑 `utils/query.py`：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'weibo_user',  # 或 'root'
    'password': 'your_password',
    'database': 'wb',
    'charset': 'utf8mb4'
}
```

## 📦 依赖安装

### 虚拟环境创建

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 依赖包安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 验证安装
pip list | grep -E "(Flask|pandas|scikit-learn|jieba)"
```

### Conda 环境（可选）

```bash
# 创建 Conda 环境
conda create -n weibo_env python=3.10
conda activate weibo_env

# 安装依赖
pip install -r requirements.txt
```

## 🕷️ 爬虫配置

### Cookie 配置（重要）

1. **获取 Cookie**
   - 打开浏览器访问 https://weibo.com
   - 按 F12 打开开发者工具
   - 切换到 Network 标签
   - 刷新页面，找到任意 weibo.com 请求
   - 复制 Request Headers 中的 Cookie 值

2. **更新配置文件**
   编辑以下文件中的 Cookie：
   - `spider/config.py`
   - `spider/improved_config.py`
   - `safe_spider_config.txt`

   ```python
   'Cookie': '你的Cookie字符串'
   ```

### 代理配置（可选）

```bash
# 获取免费代理
python spider/proxy_fetcher.py

# 测试代理
python test_spider_system.py
```

## 🌐 应用启动

### 开发模式启动

```bash
# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

# 启动应用
flask run

# 或直接运行
python app.py
```

### 自定义端口启动

```bash
# 指定端口
flask run --host=0.0.0.0 --port=8000

# 或在代码中修改
# app.py 中修改
app.run(host='0.0.0.0', port=8000, debug=True)
```

### 后台运行

```bash
# 使用 nohup
nohup python app.py &

# 或使用 screen
screen -S weibo_app
python app.py
# Ctrl+A+D 脱离
```

## 🏭 生产部署

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 参数说明
# -w 4: 4个工作进程
# -b: 绑定地址和端口
# app:app: 模块名:应用实例名
```

### 使用 uWSGI

```bash
# 安装 uWSGI
pip install uwsgi

# 创建配置文件 uwsgi.ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = 127.0.0.1:5000
chmod-socket = 664
vacuum = true
die-on-term = true

# 启动
uwsgi --ini uwsgi.ini
```

### Nginx 配置

```nginx
# /etc/nginx/sites-available/weibo_app
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/project/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL 配置（HTTPS）

```nginx
server {
    listen 443 ssl http2;
    server_name your_domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    # ... 其他配置
}
```

### Systemd 服务

创建 `/etc/systemd/system/weibo-app.service`：

```ini
[Unit]
Description=Weibo Opinion Analysis App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl start weibo-app
sudo systemctl enable weibo-app

# 查看状态
sudo systemctl status weibo-app

# 查看日志
sudo journalctl -u weibo-app -f
```

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查 MySQL 服务状态
sudo systemctl status mysql

# 检查连接
mysql -u your_user -p -h localhost wb

# 测试 Python 连接
python -c "import pymysql; pymysql.connect(host='localhost', user='your_user', password='your_pass', database='wb')"
```

#### 2. 爬虫无法获取数据
- 检查 Cookie 是否过期
- 更新 User-Agent
- 检查网络连接
- 尝试使用代理

#### 3. 应用启动失败
```bash
# 检查端口占用
netstat -tlnp | grep 5000

# 检查 Python 路径
which python
python --version

# 检查依赖
pip check
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h

# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 日志查看

```bash
# 应用日志
tail -f logs/app.log

# MySQL 日志
tail -f /var/log/mysql/error.log

# 系统日志
journalctl -f
```

### 性能优化

1. **数据库优化**
   ```sql
   -- 添加索引
   CREATE INDEX idx_created_at ON article(created_at);
   CREATE INDEX idx_user_id ON comments(user_id);
   ```

2. **应用优化**
   ```python
   # 启用缓存
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

3. **系统优化**
   ```bash
   # 增加文件描述符限制
   echo "www-data soft nofile 65536" >> /etc/security/limits.conf
   echo "www-data hard nofile 65536" >> /etc/security/limits.conf
   ```

## 📞 获取帮助

如果遇到问题，请：

1. 查看项目 Issues
2. 检查日志文件
3. 提供详细的错误信息
4. 说明你的环境配置

---

**最后更新**: 2025年9月20日