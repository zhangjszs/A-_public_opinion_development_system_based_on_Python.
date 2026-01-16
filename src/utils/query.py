#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接和查询优化模块
功能：提供高性能的数据库连接池和查询方法
特性：连接池管理、自动重连、事务支持、性能监控
作者：微博舆情分析系统
"""

from __future__ import annotations
import atexit
import threading
import time
import logging
from typing import Optional, List, Dict, Any, Union

import pymysql
from pymysql import connect
import pymysql.cursors
from pymysql.constants import CLIENT
from sqlalchemy import create_engine
import pandas as pd

# 导入统一配置模块
from config.settings import Config

# 配置日志记录器
logger = logging.getLogger(__name__)


class DatabasePool:
    """
    数据库连接池管理类
    提供高效的数据库连接管理和自动故障恢复
    """
    
    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        database: str = None,
        port: int = None,
        max_connections: int = None
    ):
        """
        初始化数据库连接池
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            port: 数据库端口
            max_connections: 最大连接数
        """
        # 从配置模块获取默认值
        host = host or Config.DB_HOST
        user = user or Config.DB_USER
        password = password or Config.DB_PASSWORD
        database = database or Config.DB_NAME
        port = port or Config.DB_PORT
        max_connections = max_connections or Config.DB_POOL_SIZE
        
        # 数据库连接配置
        self.config: Dict[str, Any] = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': Config.DB_CHARSET,            # 支持emoji和特殊字符
            'autocommit': True,                      # 自动提交事务
            'client_flag': CLIENT.MULTI_STATEMENTS,  # 支持多语句执行
            'cursorclass': pymysql.cursors.DictCursor # 返回字典格式结果
        }
        
        # 连接池管理
        self.pool = []              # 可用连接池
        self.used = []              # 正在使用的连接
        self.lock = threading.Lock() # 线程锁，保证线程安全
        self.max_connections = max_connections
        
        # 性能统计
        self.total_queries = 0
        self.failed_queries = 0
        self.start_time = time.time()
        
        # 初始化连接池 - 预创建几个连接提高响应速度
        logger.info(f"初始化数据库连接池: {database}@{host}:{port}")
        for _ in range(min(3, max_connections)):  # 初始创建3个连接或最大连接数
            self._create_connection()
        
        logger.info(f"连接池初始化完成，初始连接数: {len(self.pool)}")
    
    def _create_connection(self):
        """
        创建新的数据库连接
        包含错误处理和连接验证
        
        Returns:
            pymysql.Connection: 数据库连接对象或None
        """
        try:
            conn = pymysql.connect(**self.config)
            # 测试连接是否可用
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            self.pool.append(conn)
            logger.debug("创建新数据库连接成功")
            return conn
            
        except Exception as e:
            logger.error(f"数据库连接创建失败: {e}")
            self.failed_queries += 1
            return None
    
    def get_connection(self):
        """
        从连接池获取可用连接
        自动处理连接失效和重连
        
        Returns:
            pymysql.Connection: 数据库连接对象
        """
        with self.lock:
            # 尝试从池中获取连接
            if self.pool:
                conn = self.pool.pop()
                try:
                    # 检查连接是否有效（ping操作）
                    conn.ping(reconnect=True)
                    self.used.append(conn)
                    logger.debug("从连接池获取连接成功")
                    return conn
                except Exception as e:
                    logger.warning(f"连接池中的连接已失效: {e}")
                    # 连接失效，创建新连接
                    new_conn = self._create_connection()
                    if new_conn:
                        self.used.append(new_conn)
                    return new_conn
            
            # 连接池为空，检查是否可以创建新连接
            elif len(self.used) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self.used.append(conn)
                    logger.debug("创建新连接成功")
                return conn
            
            else:
                # 连接池已满，记录警告
                logger.warning("连接池已达到最大连接数限制")
                return None
    
    def return_connection(self, conn):
        """
        归还连接到连接池
        自动检查连接状态
        
        Args:
            conn: 要归还的数据库连接
        """
        if not conn:
            return
            
        with self.lock:
            if conn in self.used:
                self.used.remove(conn)
                
                try:
                    # 检查连接是否仍然有效
                    conn.ping(reconnect=False)
                    self.pool.append(conn)
                    logger.debug("连接归还到连接池成功")
                except:
                    # 连接已失效，直接关闭
                    try:
                        conn.close()
                    except:
                        pass
                    logger.debug("失效连接已关闭")
    
    def get_stats(self):
        """
        获取连接池统计信息
        用于性能监控和调试
        
        Returns:
            dict: 包含连接池状态的字典
        """
        with self.lock:
            uptime = time.time() - self.start_time
            success_rate = (self.total_queries - self.failed_queries) / max(self.total_queries, 1) * 100
            
            return {
                'total_queries': self.total_queries,
                'failed_queries': self.failed_queries,
                'success_rate': f"{success_rate:.2f}%",
                'available_connections': len(self.pool),
                'used_connections': len(self.used),
                'max_connections': self.max_connections,
                'uptime_hours': uptime / 3600,
                'queries_per_minute': self.total_queries / max(uptime / 60, 1)
            }
    
    def close_all(self):
        """
        关闭所有连接，清理资源
        应用退出时调用
        """
        with self.lock:
            # 关闭所有可用连接
            for conn in self.pool:
                try:
                    conn.close()
                except:
                    pass
            
            # 关闭所有正在使用的连接
            for conn in self.used:
                try:
                    conn.close()
                except:
                    pass
            
            self.pool.clear()
            self.used.clear()
            logger.info("所有数据库连接已关闭")


# 全局连接池实例 - 单例模式（使用配置文件中的参数）
db_pool = DatabasePool()

# SQLAlchemy 引擎配置 - 用于pandas DataFrame操作（使用配置文件中的参数）
engine = create_engine(
    Config.get_database_url(),
    pool_size=Config.DB_POOL_SIZE,      # 基础连接池大小
    max_overflow=20,                     # 超出连接池大小的额外连接数
    pool_recycle=Config.DB_POOL_RECYCLE, # 连接回收时间
    pool_pre_ping=True,                  # 使用前ping测试连接
    pool_timeout=Config.DB_POOL_TIMEOUT, # 获取连接的超时时间
    echo=Config.IS_DEVELOPMENT           # 开发环境打印SQL语句
)


def querys(sql, params=None, type='no_select'):
    """
    优化后的数据库查询函数
    支持参数化查询，防止SQL注入攻击
    
    Args:
        sql: SQL查询语句
        params: 查询参数列表
        type: 查询类型 ('no_select' 表示非查询操作)
        
    Returns:
        查询结果列表或执行状态消息
    """
    if params is None:
        params = []
    
    # 更新查询统计
    db_pool.total_queries += 1
    start_time = time.time()
    
    # 获取数据库连接（支持重试机制）
    conn = db_pool.get_connection()
    if not conn:
        # 第一次获取失败，等待后重试
        logger.warning("首次获取连接失败，100ms后重试...")
        time.sleep(0.1)
        conn = db_pool.get_connection()
        if not conn:
            db_pool.failed_queries += 1
            raise Exception("无法获取数据库连接，请检查数据库服务状态")
    
    try:
        with conn.cursor() as cursor:
            # 执行SQL语句（支持参数化查询防止SQL注入）
            if params:
                cursor.execute(sql, tuple(params))
            else:
                cursor.execute(sql)
            
            # 根据查询类型返回结果
            if type != 'no_select':
                # SELECT查询：返回所有结果
                data_list = cursor.fetchall()
                
                # 记录查询性能
                query_time = time.time() - start_time
                logger.debug(f"查询完成: {len(data_list)}条记录, 耗时{query_time:.3f}秒")
                
                return data_list
            else:
                # INSERT/UPDATE/DELETE操作：返回成功消息
                affected_rows = cursor.rowcount
                query_time = time.time() - start_time
                logger.debug(f"数据修改完成: 影响{affected_rows}行, 耗时{query_time:.3f}秒")
                
                return '数据库语句执行成功'
                
    except Exception as e:
        # 错误处理：记录错误并重新抛出
        db_pool.failed_queries += 1
        logger.error(f"SQL执行错误: {sql[:100]}... 参数: {params} 错误: {e}")
        raise e
        
    finally:
        # 确保连接被正确归还到连接池
        db_pool.return_connection(conn)


def query_dataframe(sql, params=None):
    """
    执行查询并返回pandas DataFrame
    适用于数据分析和大批量数据处理
    
    Args:
        sql: SQL查询语句
        params: 查询参数
        
    Returns:
        pandas.DataFrame: 查询结果数据框
    """
    start_time = time.time()
    
    try:
        # 使用SQLAlchemy引擎执行查询
        if params:
            df = pd.read_sql(sql, engine, params=params)
        else:
            df = pd.read_sql(sql, engine)
        
        # 记录查询性能
        query_time = time.time() - start_time
        logger.debug(f"DataFrame查询完成: {len(df)}行 x {len(df.columns)}列, 耗时{query_time:.3f}秒")
        
        return df
        
    except Exception as e:
        logger.error(f"DataFrame查询错误: {sql[:100]}... 错误: {e}")
        # 返回空DataFrame而不是抛出异常，保证程序稳定性
        return pd.DataFrame()


def get_database_stats():
    """
    获取数据库连接池性能统计
    用于系统监控和性能调优
    
    Returns:
        dict: 性能统计字典
    """
    return db_pool.get_stats()


# 应用退出时的清理函数
def cleanup_database() -> None:
    """应用退出时清理数据库连接池"""
    logger.info("正在关闭数据库连接池...")
    db_pool.close_all()
    # 关闭备用连接
    if _backup_connection['conn'] is not None:
        try:
            _backup_connection['conn'].close()
        except:
            pass

# 注册退出时的清理函数
atexit.register(cleanup_database)


# ========== 备用连接（懒加载模式） ==========
# 存储备用连接的字典，实现懒加载
_backup_connection: Dict[str, Any] = {'conn': None, 'cursor': None}


def get_backup_connection():
    """
    获取备用数据库连接（懒加载）
    仅在首次调用时创建连接
    
    Returns:
        tuple: (connection, cursor) 或 (None, None) 如果连接失败
    """
    if _backup_connection['conn'] is None:
        try:
            _backup_connection['conn'] = connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            _backup_connection['cursor'] = _backup_connection['conn'].cursor()
            logger.info("备用数据库连接已建立（懒加载）")
        except Exception as e:
            logger.warning(f"备用连接建立失败: {e}")
            _backup_connection['conn'] = None
            _backup_connection['cursor'] = None
    
    return _backup_connection['conn'], _backup_connection['cursor']


# 向后兼容：提供 conn 和 cursor 变量（首次访问时懒加载）
# 注意：推荐使用 get_backup_connection() 函数
conn: Optional[pymysql.Connection] = None
cursor = None