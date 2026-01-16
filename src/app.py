#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博舆情分析系统 - Flask主应用
功能：Web应用主入口，路由管理，用户认证中间件
特性：蓝图架构、会话管理、错误处理、安全防护
作者：微博舆情分析系统

系统架构：
- 用户认证：session-based认证，登录状态检查
- 路由管理：蓝图(Blueprint)模式，模块化路由
- 错误处理：自定义404页面，异常捕获
- 安全防护：路径拦截，静态文件保护
"""

from flask import Flask, session, render_template, redirect, request, jsonify
import re
import os
import time
import logging
from datetime import datetime

# 导入统一配置模块
from config.settings import Config

# 确保日志目录存在
os.makedirs(Config.LOG_DIR, exist_ok=True)

# 配置日志系统
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(Config.LOG_DIR, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 应用启动配置 =====
def create_app_directories():
    """创建应用必需的目录"""
    # 使用配置中的目录
    directories = [
        Config.LOG_DIR,
        Config.CACHE_DIR,
        os.path.join(Config.STATIC_DIR, 'uploads')
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")

# 创建Flask应用实例
app = Flask(__name__)

# ===== 应用配置 =====
# 从环境变量加载安全密钥（使用 config/settings.py 统一管理）
app.secret_key = Config.SECRET_KEY

# 根据环境变量设置调试模式
app.debug = Config.DEBUG

# 应用配置
app.config['JSON_AS_ASCII'] = Config.JSON_AS_ASCII           # 支持中文JSON响应
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = Config.SEND_FILE_MAX_AGE_DEFAULT  # 静态文件缓存时间
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH # 最大上传文件大小

# Session配置
app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME

logger.info(f"Flask应用配置加载完成 [环境: {Config.FLASK_ENV}, 调试模式: {Config.DEBUG}]")

# ===== 蓝图注册 =====
# 导入并注册应用蓝图模块
try:
    from views.page import page  # 页面视图蓝图
    from views.user import user  # 用户认证蓝图
    from views.api import api    # API视图蓝图
    
    app.register_blueprint(page.pb)  # 注册页面蓝图
    app.register_blueprint(user.ub)  # 注册用户蓝图
    app.register_blueprint(api.bp)   # 注册API蓝图
    
    logger.info("蓝图注册完成: page, user, api")
    
except ImportError as e:
    logger.error(f"蓝图导入失败: {e}")
    raise


# ===== 工具函数 =====
def is_user_logged_in():
    """
    检查用户登录状态
    
    Returns:
        bool: 用户是否已登录
    """
    return session.get('username') is not None

def get_client_ip():
    """
    获取客户端真实IP地址
    处理代理和负载均衡情况
    
    Returns:
        str: 客户端IP地址
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def log_request_info():
    """记录请求信息用于审计和调试"""
    user = session.get('username', 'Anonymous')
    ip = get_client_ip()
    logger.info(f"请求: {request.method} {request.path} | 用户: {user} | IP: {ip}")


# ===== 路由定义 =====
@app.route('/')
def index():
    """
    首页路由 - 重定向到登录页面
    确保用户必须登录才能使用系统
    """
    logger.info("访问首页，重定向到登录页面")
    return redirect('/user/login')


@app.route('/health')
def health_check():
    """
    健康检查端点
    用于监控系统状态和负载均衡健康检查
    
    Returns:
        JSON: 系统状态信息
    """
    try:
        # 检查数据库连接
        from utils.query import get_database_stats
        db_stats = get_database_stats()
        
        health_info = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            'database': {
                'connected': bool(db_stats),
                'stats': db_stats
            },
            'memory_usage': 'N/A',  # 可以添加内存使用情况
            'version': '1.0.0'
        }
        
        return jsonify(health_info)
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/session/check')
def session_check():
    """
    检查用户会话状态
    
    Returns:
        JSON: 会话状态信息
    """
    try:
        username = session.get('username')
        is_authenticated = is_user_logged_in()
        
        if is_authenticated:
            return jsonify({
                'authenticated': True,
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'sessionId': session.get('_id', 'unknown')
            })
        else:
            return jsonify({
                'authenticated': False,
                'message': '会话已过期或不存在'
            }), 401
            
    except Exception as e:
        logger.error(f"会话检查失败: {e}")
        return jsonify({
            'authenticated': False,
            'error': '会话检查过程中发生错误'
        }), 500


@app.route('/api/session/extend', methods=['POST'])
def session_extend():
    """
    延长用户会话
    
    Returns:
        JSON: 延长结果
    """
    try:
        if not is_user_logged_in():
            return jsonify({
                'success': False,
                'message': '用户未登录，无法延长会话'
            }), 401
        
        # 更新会话的permanent标志，重新设置过期时间
        session.permanent = True
        
        # 记录会话延长操作
        username = session.get('username')
        logger.info(f"用户 {username} 延长会话 | IP: {get_client_ip()}")
        
        return jsonify({
            'success': True,
            'message': '会话已成功延长',
            'timestamp': datetime.now().isoformat(),
            'username': username
        })
        
    except Exception as e:
        logger.error(f"会话延长失败: {e}")
        return jsonify({
            'success': False,
            'error': '会话延长过程中发生错误'
        }), 500


# ===== 中间件和钩子函数 =====
@app.before_request
def before_request():
    """
    请求前置处理中间件
    
    功能：
    1. 静态资源直接放行
    2. 登录/注册页面无需认证
    3. 健康检查端点无需认证
    4. 其他页面需要登录验证
    5. 记录请求日志
    """
    # 记录请求信息
    log_request_info()
    
    # 静态资源放行（CSS、JS、图片等）
    if request.path.startswith('/static'):
        return None
    
    # 公开访问的端点（无需登录）
    public_endpoints = [
        '/user/login',      # 登录页面
        '/user/register',   # 注册页面
        '/health',          # 健康检查
        '/'                 # 首页（会重定向到登录）
    ]
    
    if request.path in public_endpoints:
        return None
    
    # API端点特殊处理
    if request.path.startswith('/api/'):
        if not is_user_logged_in():
            return jsonify({
                'error': 'Unauthorized',
                'message': '请先登录',
                'code': 401
            }), 401
        return None
    
    # 其他页面需要登录验证
    if not is_user_logged_in():
        logger.warning(f"未登录访问受保护页面: {request.path} | IP: {get_client_ip()}")
        
        # 保存当前请求的URL，登录后可以重定向回来
        if request.method == 'GET' and not request.path.startswith('/api/'):
            redirect_url = request.path
            if request.query_string:
                redirect_url += '?' + request.query_string.decode('utf-8')
            return redirect(f'/user/login?redirect={redirect_url}')
        else:
            return redirect('/user/login')
    
    return None


@app.after_request
def after_request(response):
    """
    请求后置处理中间件
    
    功能：
    1. 添加安全响应头
    2. 处理跨域请求
    3. 记录响应状态
    
    Args:
        response: Flask响应对象
        
    Returns:
        response: 处理后的响应对象
    """
    # 添加安全响应头
    response.headers['X-Content-Type-Options'] = 'nosniff'      # 防止MIME类型嗅探
    response.headers['X-Frame-Options'] = 'DENY'               # 防止页面被嵌入iframe
    response.headers['X-XSS-Protection'] = '1; mode=block'     # XSS保护
    
    # 缓存控制（根据内容类型）
    if request.path.startswith('/static'):
        response.headers['Cache-Control'] = 'public, max-age=300'  # 静态文件缓存5分钟
    else:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # 页面不缓存
    
    # 记录响应状态
    if response.status_code >= 400:
        logger.warning(f"响应错误: {response.status_code} | 路径: {request.path}")
    
    return response


# ===== 错误处理器 =====
@app.errorhandler(404)
def page_not_found(error):
    """
    404错误处理器
    当访问不存在的页面时显示友好的错误页面
    
    Args:
        error: 错误对象
        
    Returns:
        tuple: (模板, 状态码)
    """
    logger.warning(f"404错误: {request.path} | IP: {get_client_ip()}")
    
    # API请求返回JSON错误
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Not Found',
            'message': '请求的资源不存在',
            'code': 404,
            'path': request.path
        }), 404
    
    # 网页请求返回HTML错误页面
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    """
    500错误处理器
    处理服务器内部错误
    
    Args:
        error: 错误对象
        
    Returns:
        tuple: (响应, 状态码)
    """
    logger.error(f"500错误: {error} | 路径: {request.path} | IP: {get_client_ip()}")
    
    # API请求返回JSON错误
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Internal Server Error',
            'message': '服务器内部错误，请稍后重试',
            'code': 500
        }), 500
    
    # 网页请求返回错误页面
    try:
        return render_template('error.html', error_message='服务器内部错误'), 500
    except:
        # 如果模板加载失败，返回纯文本
        return '服务器内部错误，请稍后重试', 500


@app.errorhandler(403)
def forbidden(error):
    """
    403错误处理器
    处理权限不足错误
    """
    logger.warning(f"403错误: 权限不足 | 路径: {request.path} | IP: {get_client_ip()}")
    
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Forbidden',
            'message': '权限不足',
            'code': 403
        }), 403
    
    return render_template('error.html', error_message='权限不足'), 403


# ===== 通用路由捕获 =====
@app.route('/<path:path>')
def catch_all(path):
    """
    捕获所有未定义的路径
    重定向到404页面，防止暴露系统信息
    
    Args:
        path: 请求的路径
        
    Returns:
        redirect: 重定向到404页面
    """
    logger.info(f"捕获未定义路径: /{path} | IP: {get_client_ip()}")
    
    # 一些常见的恶意请求路径，直接拒绝
    malicious_patterns = [
        r'\.php$',           # PHP文件
        r'wp-admin',         # WordPress后台
        r'phpmyadmin',       # phpMyAdmin
        r'\.env$',           # 环境变量文件
        r'\.git',            # Git仓库
        r'admin\.php',       # 管理页面
        r'login\.php',       # PHP登录页面
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, path, re.IGNORECASE):
            logger.warning(f"检测到可疑请求: /{path} | IP: {get_client_ip()}")
            return '', 404  # 直接返回404，不提供任何信息
    
    # 正常的404重定向
    return redirect('/404')


# ===== 应用启动配置 =====


def initialize_app():
    """初始化应用"""
    # 记录启动时间
    app.start_time = time.time()
    
    # 创建必要目录
    create_app_directories()
    
    # 记录启动信息
    logger.info("=" * 50)
    logger.info("微博舆情分析系统启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"调试模式: {'开启' if app.debug else '关闭'}")
    logger.info(f"Python版本: {os.sys.version}")
    logger.info("=" * 50)


# ===== 主程序入口 =====
if __name__ == '__main__':
    try:
        # 初始化应用
        initialize_app()
        
        # 启动Flask开发服务器
        # 生产环境请使用gunicorn或uwsgi等WSGI服务器
        app.run(
            host='127.0.0.1',        # 监听地址（生产环境可设为0.0.0.0）
            port=5000,               # 监听端口
            debug=Config.DEBUG,      # 从配置读取调试模式
            threaded=True,           # 支持多线程
            use_reloader=Config.IS_DEVELOPMENT  # 仅开发环境启用自动重载
        )
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    finally:
        logger.info("应用已停止")
