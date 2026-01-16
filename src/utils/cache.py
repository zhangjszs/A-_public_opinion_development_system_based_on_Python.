# -*- coding: utf-8 -*-
"""
缓存管理模块
提供内存缓存和文件缓存功能来提升性能
"""

import json
import pickle
import os
import time
import hashlib
from functools import wraps
from threading import Lock

class MemoryCache:
    """内存缓存类"""
    def __init__(self, default_timeout=300):  # 默认5分钟过期
        self.cache = {}
        self.timestamps = {}
        self.default_timeout = default_timeout
        self.lock = Lock()
    
    def _generate_key(self, func_name, args, kwargs):
        """生成缓存键"""
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """获取缓存"""
        with self.lock:
            if key in self.cache:
                timestamp = self.timestamps.get(key, 0)
                if time.time() - timestamp < self.default_timeout:
                    return self.cache[key]
                else:
                    # 过期删除
                    del self.cache[key]
                    del self.timestamps[key]
            return None
    
    def set(self, key, value, timeout=None):
        """设置缓存"""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self):
        """获取缓存大小"""
        return len(self.cache)

class FileCache:
    """文件缓存类"""
    def __init__(self, cache_dir='./cache', default_timeout=3600):  # 默认1小时过期
        self.cache_dir = cache_dir
        self.default_timeout = default_timeout
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_path(self, key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get(self, key):
        """获取文件缓存"""
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            # 检查是否过期
            if time.time() - os.path.getmtime(cache_path) < self.default_timeout:
                try:
                    with open(cache_path, 'rb') as f:
                        return pickle.load(f)
                except:
                    # 读取失败，删除文件
                    os.remove(cache_path)
            else:
                # 过期删除
                os.remove(cache_path)
        return None
    
    def set(self, key, value):
        """设置文件缓存"""
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"缓存写入失败: {e}")
    
    def clear(self):
        """清空文件缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                os.remove(os.path.join(self.cache_dir, filename))

# 全局缓存实例
memory_cache = MemoryCache(default_timeout=300)  # 内存缓存5分钟
file_cache = FileCache(default_timeout=1800)     # 文件缓存30分钟

def cache_result(timeout=300, use_file_cache=False):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # 先尝试内存缓存
            result = memory_cache.get(cache_key)
            if result is not None:
                return result
            
            # 再尝试文件缓存
            if use_file_cache:
                result = file_cache.get(cache_key)
                if result is not None:
                    # 同时写入内存缓存
                    memory_cache.set(cache_key, result, timeout)
                    return result
            
            # 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            # 写入缓存
            memory_cache.set(cache_key, result, timeout)
            if use_file_cache:
                file_cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

def clear_all_cache():
    """清空所有缓存"""
    memory_cache.clear()
    file_cache.clear()
    print("所有缓存已清空")

def get_cache_info():
    """获取缓存信息"""
    return {
        'memory_cache_size': memory_cache.size(),
        'file_cache_dir': file_cache.cache_dir,
        'file_cache_count': len([f for f in os.listdir(file_cache.cache_dir) if f.endswith('.cache')])
    }