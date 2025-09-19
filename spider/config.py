#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博爬虫配置管理模块
功能：集中管理爬虫配置、请求头、代理池和反反爬机制
特性：动态配置、代理轮换、智能重试、性能监控
作者：微博舆情分析系统

使用说明：
1. 首次使用前请更新HEADERS中的Cookie和User-Agent
2. 运行proxy_fetcher.py获取免费代理IP
3. 根据需要调整请求频率和超时参数
"""

import random
import requests
import time
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志记录器
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpiderConfigManager:
    """
    爬虫配置管理器
    统一管理所有爬虫相关配置和工具方法
    """
    
    def __init__(self):
        """初始化配置管理器"""
        
        # ===== 核心请求头配置 =====
        # !!!重要提示!!!
        # 请定期更新以下Cookie和User-Agent：
        # 1. 访问 https://weibo.com 并登录
        # 2. F12开发者工具 → Network → 复制请求头
        # 3. 更新下面的Cookie值（关键）
        self.BASE_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Cookie': 'SCF=AqCRsFqi8WAJrUmJsIl2VW5wy0cNAmgxzPmVBKom1Y2_dhFsEAuNwmOs42nG9FqoaluPcFcpm0jfaAxrUgOIQSM.; XSRF-TOKEN=1h5takIcR4o8S-XoHMy-_iss; PC_TOKEN=381e9e398d; SUB=_2A25FyHk_DeRhGeBP7FoT9irFzT6IHXVmpPT3rDV8PUNbmtAbLWPjkW9NRSeoOZRWQmlb1AmSRr_dMYyHd9S1cwEO; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWrjdM87V-QDpZZbG1A5myw5JpX5KzhUgL.FoqpS0nESoB4Soz2dJLoI05LxK-L1K5L12BLxK-LB-BL1KMLxK.L1hML12BLxKnLBKqL1h2LxK-L1K5L1KUNUNMt; ALF=02_1760794223; WBPSESS=9V-YExyHWqKmx5h49Sox-kf-XeX6_S703-gbU6Af-Yg2IOcoO0zVOpBVEtRgHPDtdCYzJiBAkRN0y8M6PXKgD3vaIz8QmwHbdTZGnF9qh4L10Xo4pZuSs59dd036b3UxQwwb2uXCTFIT2m8RarQhRA==',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # ===== User-Agent池配置 =====
        # 包含主流浏览器的最新版本，定期更新以保持真实性
        self.USER_AGENTS = [
            # Windows Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            
            # Windows Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
            
            # Windows Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            
            # macOS Chrome
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            
            # macOS Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        # ===== 代理配置 =====
        self.USE_PROXY = True                    # 是否启用代理
        self.PROXY_FILE = 'spider/working_proxies.json'  # 代理文件路径
        self.working_proxies = []                # 可用代理列表
        self.proxy_lock = threading.Lock()       # 代理操作线程锁
        
        # ===== 请求参数配置 =====
        self.DEFAULT_TIMEOUT = 45  # 增加到45秒               # 默认超时时间（秒）
        self.DEFAULT_DELAY = (15, 30)  # 修改为15-30秒，避免403错误             # 请求间隔范围（秒）
        self.MAX_RETRIES = 3                    # 最大重试次数
        self.RETRY_DELAY = 5                    # 重试间隔（秒）
        
        # ===== 反反爬配置 =====
        self.RANDOM_HEADER_FIELDS = {
            'Sec-CH-UA': [
                '"Not_A Brand";v="8", "Chromium";v="139", "Google Chrome";v="139"',
                '"Not(A:Brand";v="24", "Chromium";v="139"',
                '"Chromium";v="139", "Not=A?Brand";v="24"'
            ],
            'Sec-CH-UA-Mobile': ['?0', '?1'],
            'Sec-CH-UA-Platform': ['"Windows"', '"macOS"', '"Linux"'],
        }
        
        # ===== 性能统计 =====
        self.request_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.start_time = time.time()
        
        # 初始化配置
        self._initialize()
    
    def _initialize(self):
        """初始化配置管理器"""
        # 加载可用代理
        self._load_working_proxies()
        
        # 创建代理文件目录
        proxy_dir = os.path.dirname(self.PROXY_FILE)
        if proxy_dir and not os.path.exists(proxy_dir):
            os.makedirs(proxy_dir)
        
        logger.info("爬虫配置管理器初始化完成")
        logger.info(f"可用代理数量: {len(self.working_proxies)}")
    
    def _load_working_proxies(self):
        """从文件加载可用代理列表"""
        try:
            if os.path.exists(self.PROXY_FILE):
                with open(self.PROXY_FILE, 'r', encoding='utf-8') as f:
                    self.working_proxies = json.load(f)
                logger.info(f"加载了 {len(self.working_proxies)} 个保存的代理")
            else:
                logger.info("代理文件不存在，将使用直连模式")
                self.working_proxies = []
        except Exception as e:
            logger.error(f"加载代理文件失败: {e}")
            self.working_proxies = []
    
    def _save_working_proxies(self):
        """保存可用代理列表到文件"""
        try:
            with open(self.PROXY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.working_proxies, f, indent=2, ensure_ascii=False)
            logger.debug(f"保存了 {len(self.working_proxies)} 个可用代理")
        except Exception as e:
            logger.error(f"保存代理文件失败: {e}")
    
    def get_random_user_agent(self):
        """
        获取随机User-Agent
        
        Returns:
            str: 随机选择的User-Agent字符串
        """
        return random.choice(self.USER_AGENTS)
    
    def get_random_headers(self):
        """
        获取随机化的请求头
        每次请求使用不同的User-Agent和可选头部字段
        
        Returns:
            dict: 随机化的请求头字典
        """
        headers = self.BASE_HEADERS.copy()
        
        # 随机User-Agent
        headers['User-Agent'] = self.get_random_user_agent()
        
        # 随机添加可选的反指纹识别头部
        for field, values in self.RANDOM_HEADER_FIELDS.items():
            if random.random() > 0.3:  # 70%概率添加
                headers[field] = random.choice(values)
        
        # 随机调整部分头部顺序（模拟不同浏览器行为）
        if random.random() > 0.5:
            headers['Accept-Encoding'] = 'gzip, deflate'
        
        return headers
    
    def test_proxy(self, proxy_ip, test_url='http://httpbin.org/ip', timeout=10):
        """
        测试代理IP的可用性
        
        Args:
            proxy_ip: 代理地址 (格式: "ip:port")
            test_url: 测试URL
            timeout: 测试超时时间
            
        Returns:
            bool: 代理是否可用
        """
        try:
            proxy_dict = {
                'http': f'http://{proxy_ip}',
                'https': f'http://{proxy_ip}'
            }
            
            headers = self.get_random_headers()
            response = requests.get(
                test_url,
                proxies=proxy_dict,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"代理测试成功: {proxy_ip} → IP: {result.get('origin', 'Unknown')}")
                return True
            else:
                logger.debug(f"代理测试失败: {proxy_ip} (状态码: {response.status_code})")
                return False
                
        except Exception as e:
            logger.debug(f"代理测试异常: {proxy_ip} ({e})")
            return False
    
    def add_proxy(self, proxy_ip):
        """
        添加新代理到可用列表
        自动测试可用性
        
        Args:
            proxy_ip: 代理地址
        """
        if proxy_ip not in self.working_proxies:
            if self.test_proxy(proxy_ip):
                with self.proxy_lock:
                    self.working_proxies.append(proxy_ip)
                    self._save_working_proxies()
                logger.info(f"添加可用代理: {proxy_ip}")
                return True
            else:
                logger.warning(f"代理不可用: {proxy_ip}")
                return False
        return True
    
    def get_working_proxy(self):
        """
        获取一个可用的代理配置
        自动测试和清理失效代理
        
        Returns:
            dict: 代理配置字典，失败返回None
        """
        if not self.USE_PROXY or not self.working_proxies:
            return None
        
        with self.proxy_lock:
            # 最多尝试3个代理
            for _ in range(min(3, len(self.working_proxies))):
                if not self.working_proxies:
                    break
                
                proxy_ip = random.choice(self.working_proxies)
                
                # 快速测试代理（短超时）
                if self.test_proxy(proxy_ip, timeout=5):
                    return {
                        'http': f'http://{proxy_ip}',
                        'https': f'http://{proxy_ip}'
                    }
                else:
                    # 移除失效代理
                    self.working_proxies.remove(proxy_ip)
                    self._save_working_proxies()
                    logger.info(f"移除失效代理: {proxy_ip}")
            
            logger.warning("未找到可用代理，将使用直连")
            return None
    
    def make_safe_request(self, url, method='GET', use_proxy=True, **kwargs):
        """
        发起安全的HTTP请求
        集成重试、代理、反反爬等机制
        
        Args:
            url: 请求URL
            method: HTTP方法
            use_proxy: 是否使用代理
            **kwargs: requests库的其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        self.request_count += 1
        
        # 设置默认参数
        kwargs.setdefault('headers', self.get_random_headers())
        kwargs.setdefault('timeout', self.DEFAULT_TIMEOUT)
        
        # 请求间隔（反反爬）
        delay = random.uniform(*self.DEFAULT_DELAY)
        logger.debug(f"请求延迟: {delay:.2f}秒")
        time.sleep(delay)
        
        # 重试机制
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                # 设置代理
                if use_proxy and self.USE_PROXY:
                    proxy = self.get_working_proxy()
                    if proxy:
                        kwargs['proxies'] = proxy
                        logger.debug(f"使用代理: {proxy['http']}")
                    else:
                        kwargs.pop('proxies', None)
                        logger.debug("使用直连")
                else:
                    kwargs.pop('proxies', None)
                
                # 发起请求
                response = requests.request(method, url, **kwargs)
                
                # 状态检查
                if response.status_code == 200:
                    self.success_count += 1
                    logger.debug(f"请求成功: {url[:80]}...")
                    return response
                elif response.status_code == 403:
                    logger.warning(f"请求被拒绝(403): 可能触发反爬机制")
                    raise Exception("403 Forbidden - 反爬机制触发")
                elif response.status_code == 429:
                    logger.warning(f"请求频率过高(429): 需要降低请求频率")
                    raise Exception("429 Too Many Requests - 请求过于频繁")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.MAX_RETRIES}): {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    retry_delay = self.RETRY_DELAY * (attempt + 1)  # 递增延迟
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    
                    # 移除当前代理（如果使用了代理）
                    if 'proxies' in kwargs:
                        current_proxy = kwargs.get('proxies', {}).get('http', '')
                        if current_proxy:
                            proxy_ip = current_proxy.replace('http://', '')
                            with self.proxy_lock:
                                if proxy_ip in self.working_proxies:
                                    self.working_proxies.remove(proxy_ip)
                                    logger.info(f"移除当前失效代理: {proxy_ip}")
        
        # 所有重试失败
        self.failed_count += 1
        logger.error(f"请求最终失败: {url}")
        raise last_exception
    
    def get_config_stats(self):
        """
        获取配置统计信息
        
        Returns:
            dict: 统计信息字典
        """
        uptime = time.time() - self.start_time
        success_rate = (self.success_count / max(self.request_count, 1)) * 100
        
        return {
            'user_agents_count': len(self.USER_AGENTS),
            'working_proxies_count': len(self.working_proxies),
            'total_requests': self.request_count,
            'success_requests': self.success_count,
            'failed_requests': self.failed_count,
            'success_rate': f"{success_rate:.2f}%",
            'uptime_hours': uptime / 3600,
            'requests_per_hour': self.request_count / max(uptime / 3600, 1),
            'proxy_enabled': self.USE_PROXY,
            'default_timeout': self.DEFAULT_TIMEOUT,
            'delay_range': self.DEFAULT_DELAY,
            'max_retries': self.MAX_RETRIES
        }
    
    def update_headers(self, new_headers):
        """
        更新基础请求头
        
        Args:
            new_headers: 新的请求头字典
        """
        self.BASE_HEADERS.update(new_headers)
        logger.info("请求头已更新")
    
    def reload_proxies(self):
        """重新加载代理列表"""
        self._load_working_proxies()
        logger.info(f"重新加载代理完成，当前可用: {len(self.working_proxies)} 个")


# ===== 全局配置实例 =====
_config_manager = None

def get_config_manager():
    """
    获取全局配置管理器实例（单例模式）
    
    Returns:
        SpiderConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = SpiderConfigManager()
    return _config_manager


# ===== 向后兼容的接口函数 =====
def get_random_user_agent():
    """获取随机User-Agent（向后兼容）"""
    return get_config_manager().get_random_user_agent()

def get_random_headers():
    """获取随机请求头（向后兼容）"""
    return get_config_manager().get_random_headers()

def get_proxy():
    """获取代理配置（向后兼容）"""
    return get_config_manager().get_working_proxy()

def get_working_proxy():
    """获取可用代理（向后兼容）"""
    return get_config_manager().get_working_proxy()

def test_proxy(proxy_dict):
    """测试代理（向后兼容）"""
    if not proxy_dict:
        return True
    
    manager = get_config_manager()
    proxy_ip = proxy_dict.get('http', '').replace('http://', '')
    return manager.test_proxy(proxy_ip)


# ===== 全局变量（向后兼容） =====
# 获取配置管理器实例
config_manager = get_config_manager()

# 导出常用配置
HEADERS = config_manager.BASE_HEADERS
USER_AGENTS = config_manager.USER_AGENTS
DEFAULT_TIMEOUT = config_manager.DEFAULT_TIMEOUT
DEFAULT_DELAY = config_manager.DEFAULT_DELAY