#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高性能缓存系统模块
功能：提供内存缓存和文件缓存两套机制，显著提升系统性能
特性：LRU算法、过期机制、序列化存储、线程安全、性能监控
作者：微博舆情分析系统

缓存策略：
- 内存缓存：快速访问，适合小数据量和高频访问
- 文件缓存：持久化存储，适合大数据量和跨进程共享
- 智能选择：根据数据大小和访问模式自动选择缓存策略
"""

import os
import json
import pickle
import hashlib
import time
import threading
from datetime import datetime, timedelta
from collections import OrderedDict
from functools import wraps
import logging
import sys

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LRUCache:
    """
    基于LRU(Least Recently Used)算法的内存缓存
    自动淘汰最久未使用的缓存项，防止内存溢出
    """
    
    def __init__(self, max_size=1000, default_ttl=300):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存项数量
            default_ttl: 默认缓存时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()  # 有序字典，维护访问顺序
        self.expire_times = {}      # 存储过期时间
        self.lock = threading.RLock()  # 可重入锁，保证线程安全
        
        # 性能统计
        self.hits = 0               # 命中次数
        self.misses = 0             # 未命中次数
        self.evictions = 0          # 淘汰次数
        self.start_time = time.time()
        
        logger.debug(f"LRU缓存初始化: max_size={max_size}, default_ttl={default_ttl}秒")
    
    def _is_expired(self, key):
        """
        检查缓存项是否过期
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否过期
        """
        if key not in self.expire_times:
            return True
        return time.time() > self.expire_times[key]
    
    def _evict_expired(self):
        """清理所有过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key for key, expire_time in self.expire_times.items()
            if current_time > expire_time
        ]
        
        for key in expired_keys:
            self._remove_item(key)
            logger.debug(f"清理过期缓存: {key}")
    
    def _remove_item(self, key):
        """
        移除缓存项
        
        Args:
            key: 要移除的键
        """
        if key in self.cache:
            del self.cache[key]
        if key in self.expire_times:
            del self.expire_times[key]
    
    def _evict_lru(self):
        """根据LRU算法淘汰最久未使用的缓存项"""
        if len(self.cache) >= self.max_size:
            # 移除最久未使用的项（OrderedDict的第一项）
            oldest_key = next(iter(self.cache))
            self._remove_item(oldest_key)
            self.evictions += 1
            logger.debug(f"LRU淘汰缓存: {oldest_key}")
    
    def get(self, key, default=None):
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        with self.lock:
            # 清理过期项
            self._evict_expired()
            
            if key in self.cache and not self._is_expired(key):
                # 命中：移动到末尾（标记为最近使用）
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hits += 1
                logger.debug(f"缓存命中: {key}")
                return value
            else:
                # 未命中
                self.misses += 1
                if key in self.cache:
                    self._remove_item(key)  # 移除过期项
                logger.debug(f"缓存未命中: {key}")
                return default
    
    def set(self, key, value, ttl=None):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None表示使用默认TTL
        """
        with self.lock:
            # 设置过期时间
            ttl = ttl or self.default_ttl
            expire_time = time.time() + ttl
            
            # 如果键已存在，先移除
            if key in self.cache:
                self._remove_item(key)
            
            # 检查是否需要淘汰
            self._evict_lru()
            
            # 添加新项
            self.cache[key] = value
            self.expire_times[key] = expire_time
            
            logger.debug(f"缓存设置: {key}, TTL={ttl}秒")
    
    def delete(self, key):
        """
        删除缓存项
        
        Args:
            key: 要删除的键
            
        Returns:
            bool: 是否成功删除
        """
        with self.lock:
            if key in self.cache:
                self._remove_item(key)
                logger.debug(f"缓存删除: {key}")
                return True
            return False
    
    def clear(self):
        """清空所有缓存"""
        with self.lock:
            self.cache.clear()
            self.expire_times.clear()
            logger.info("清空所有内存缓存")
    
    def size(self):
        """
        获取当前缓存大小
        
        Returns:
            int: 缓存项数量
        """
        with self.lock:
            self._evict_expired()
            return len(self.cache)
    
    def get_stats(self):
        """
        获取缓存统计信息
        
        Returns:
            dict: 统计信息字典
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / max(total_requests, 1)) * 100
            uptime = time.time() - self.start_time
            
            return {
                'type': 'LRU Memory Cache',
                'max_size': self.max_size,
                'current_size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': f"{hit_rate:.2f}%",
                'evictions': self.evictions,
                'uptime_hours': uptime / 3600,
                'requests_per_second': total_requests / max(uptime, 1)
            }


def cache_result(ttl=300, use_file_cache=False, key_func=None):
    """
    缓存装饰器
    自动缓存函数结果，提升性能
    
    Args:
        ttl: 缓存时间（秒）
        use_file_cache: 是否使用文件缓存
        key_func: 自定义键生成函数
        
    Returns:
        装饰器函数
    """
    # 创建缓存实例
    _cache = LRUCache(max_size=1000, default_ttl=ttl)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成逻辑
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = "_".join(key_parts)
            
            # 尝试从缓存获取结果
            cached_result = _cache.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"缓存命中: {func.__name__}")
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            
            logger.debug(f"缓存设置: {func.__name__}")
            return result
        
        return wrapper
    return decorator


# 导出主要接口
__all__ = ['LRUCache', 'cache_result']