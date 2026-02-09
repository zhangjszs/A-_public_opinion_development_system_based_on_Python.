#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理模块
功能：从环境变量或 .env 文件加载配置
作者：微博舆情分析系统

使用方法：
    from config.settings import Config
    print(Config.DB_HOST)
"""

import os
import secrets
from pathlib import Path
from typing import Optional

# 定义项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试加载 python-dotenv（如果安装了的话）
try:
    from dotenv import load_dotenv
    # 查找项目根目录的 .env 文件
    # settings.py 在 src/config/ 目录下，所以需要向上两级到项目根目录
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"已加载环境变量文件: {env_path}")
    else:
        print(f"警告: 未找到 .env 文件，路径: {env_path}")
except ImportError:
    pass  # python-dotenv 未安装，仅使用环境变量


def get_env(key: str, default: Optional[str] = None, cast_type: type = str):
    """
    获取环境变量值，支持类型转换
    
    Args:
        key: 环境变量名
        default: 默认值
        cast_type: 目标类型（str, int, bool, float）
    
    Returns:
        转换后的环境变量值
    """
    value = os.environ.get(key, default)
    
    if value is None:
        return None
    
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        return int(value)
    elif cast_type == float:
        return float(value)
    else:
        return str(value)


class Config:
    """应用配置类"""
    
    # ========== Flask 配置 ==========
    BASE_DIR = BASE_DIR
    
    # 标准目录配置
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODEL_DIR = os.path.join(BASE_DIR, 'src', 'model')  # 修正为 src/model
    STATIC_DIR = os.path.join(BASE_DIR, 'src', 'static')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    SPIDER_DIR = os.path.join(BASE_DIR, 'src', 'spider')
    CACHE_DIR = os.path.join(BASE_DIR, 'cache')
    
    # 确保关键目录存在
    for _dir in [DATA_DIR, MODEL_DIR, LOG_DIR, CACHE_DIR]:
        os.makedirs(_dir, exist_ok=True)

    # ========== 微博账号配置 ==========
    # 默认值留空，优先从环境变量加载
    WEIBO_COOKIE: str = get_env('WEIBO_COOKIE', '')
    WEIBO_USER_AGENT: str = get_env('WEIBO_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


    # 如果没有设置环境变量，则生成一个随机密钥（仅用于开发环境）
    SECRET_KEY: str = get_env('SECRET_KEY') or secrets.token_hex(32)
    
    # Flask 运行环境
    FLASK_ENV: str = get_env('FLASK_ENV', 'production')
    
    # 调试模式
    DEBUG: bool = get_env('DEBUG', 'False', bool)
    
    # 是否为开发环境
    IS_DEVELOPMENT: bool = FLASK_ENV == 'development'
    
    # ========== 数据库配置 ==========
    DB_HOST: str = get_env('DB_HOST', 'localhost')
    DB_PORT: int = get_env('DB_PORT', '3306', int)
    DB_USER: str = get_env('DB_USER', 'root')
    DB_PASSWORD: str = get_env('DB_PASSWORD', '')
    DB_NAME: str = get_env('DB_NAME', 'wb')
    DB_CHARSET: str = 'utf8mb4'
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = get_env('DB_POOL_SIZE', '10', int)
    DB_POOL_RECYCLE: int = 3600  # 连接回收时间（秒）
    DB_POOL_TIMEOUT: int = 30    # 获取连接超时时间（秒）
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取 SQLAlchemy 数据库连接 URL"""
        return (
            f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
            f"?charset={cls.DB_CHARSET}"
        )
    
    @classmethod
    def get_pymysql_config(cls) -> dict:
        """获取 PyMySQL 连接配置字典"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': cls.DB_CHARSET,
        }
    
    # ========== 爬虫配置 ==========
    SPIDER_TIMEOUT: int = get_env('SPIDER_TIMEOUT', '30', int)
    SPIDER_DELAY: float = get_env('SPIDER_DELAY', '2', float)
    SPIDER_RETRIES: int = get_env('SPIDER_RETRIES', '3', int)
    SPIDER_USE_PROXY: bool = get_env('SPIDER_USE_PROXY', 'False', bool)
    
    # ========== 情感分析 / LLM 配置 ==========
    LLM_API_KEY: str = get_env('LLM_API_KEY', '')
    LLM_API_URL: str = get_env('LLM_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    LLM_MODEL: str = get_env('LLM_MODEL', 'deepseek-chat')
    LLM_TIMEOUT: int = get_env('LLM_TIMEOUT', '10', int)  # LLM调用超时时间
    LLM_CACHE_TTL: int = get_env('LLM_CACHE_TTL', '3600', int)  # LLM结果缓存时间（秒）
    
    # ========== Redis配置（用于Celery和缓存） ==========
    REDIS_HOST: str = get_env('REDIS_HOST', 'localhost')
    REDIS_PORT: int = get_env('REDIS_PORT', '6379', int)
    REDIS_DB: int = get_env('REDIS_DB', '0', int)
    REDIS_PASSWORD: str = get_env('REDIS_PASSWORD', '')
    
    @classmethod
    def get_redis_url(cls) -> str:
        """获取Redis连接URL"""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    # 兼容Celery配置
    REDIS_URL: str = get_env('REDIS_URL', '')
    
    # ========== 日志配置 ==========
    LOG_LEVEL: str = get_env('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ========== 应用配置 ==========
    JSON_AS_ASCII: bool = False              # 支持中文 JSON 响应
    SEND_FILE_MAX_AGE_DEFAULT: int = 300     # 静态文件缓存时间（秒）
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 最大上传文件大小（16MB）
    PERMANENT_SESSION_LIFETIME: int = 3600   # Session 有效期（1小时）


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # 生产环境必须设置 SECRET_KEY
    @classmethod
    def validate(cls):
        if not os.environ.get('SECRET_KEY'):
            raise ValueError(
                "生产环境必须设置 SECRET_KEY 环境变量！"
                "请使用: python -c \"import secrets; print(secrets.token_hex(32))\" 生成"
            )
    
    # 生产环境Session安全配置
    SESSION_COOKIE_SECURE = True  # 仅HTTPS传输Cookie
    SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问
    SESSION_COOKIE_SAMESITE = 'Strict'  # 最严格的CSRF保护


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}


def get_config(env: Optional[str] = None):
    """
    获取当前环境的配置类
    
    Args:
        env: 环境名称，如果为 None 则从环境变量读取
    
    Returns:
        配置类
    """
    env = env or os.environ.get('FLASK_ENV', 'production')
    return config_map.get(env, ProductionConfig)
