#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感分析异步任务模块
功能：批量情感分析、LLM降级缓存
"""

import os
import sys
import json
import hashlib
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import current_task
from tasks.celery_config import celery_app
from config.settings import Config

logger = logging.getLogger(__name__)

# 尝试导入Redis（可选依赖）
try:
    import redis
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
        decode_responses=True
    )
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis连接失败: {e}")
    redis_client = None
    REDIS_AVAILABLE = False


def get_cache_key(text: str, mode: str = 'smart') -> str:
    """生成缓存键"""
    key_data = f"sentiment:{mode}:{text}"
    return hashlib.md5(key_data.encode()).hexdigest()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def analyze_sentiment_batch(self, texts: List[str], mode: str = 'smart') -> Dict[str, Any]:
    """
    批量情感分析任务
    
    Args:
        texts: 待分析文本列表
        mode: 分析模式 (simple/smart/custom)
        
    Returns:
        dict: 批量分析结果
    """
    task_id = self.request.id
    logger.info(f"[任务{task_id}] 批量情感分析: {len(texts)}条文本, mode={mode}")
    
    results = []
    cached_count = 0
    llm_count = 0
    
    try:
        from services.sentiment_service import SentimentService
        
        for i, text in enumerate(texts):
            # 更新进度
            if i % 10 == 0:  # 每10条更新一次
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i,
                        'total': len(texts),
                        'status': f'已处理 {i}/{len(texts)} 条'
                    }
                )
            
            # 尝试从缓存获取
            if REDIS_AVAILABLE and mode == 'smart':
                cache_key = get_cache_key(text, mode)
                cached = redis_client.get(cache_key)
                if cached:
                    result = json.loads(cached)
                    result['cached'] = True
                    results.append(result)
                    cached_count += 1
                    continue
            
            # 调用分析服务
            result = SentimentService.analyze(text, mode)
            result['cached'] = False
            results.append(result)
            
            if mode == 'smart':
                llm_count += 1
                # 写入缓存
                if REDIS_AVAILABLE:
                    cache_key = get_cache_key(text, mode)
                    redis_client.setex(
                        cache_key,
                        Config.LLM_CACHE_TTL,
                        json.dumps(result)
                    )
        
        return {
            'status': 'success',
            'task_id': task_id,
            'total': len(texts),
            'cached': cached_count,
            'llm_calls': llm_count,
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"[任务{task_id}] 批量分析失败: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_single_with_fallback(self, text: str, mode: str = 'smart') -> Dict[str, Any]:
    """
    单条文本分析（带降级缓存）
    
    Args:
        text: 待分析文本
        mode: 分析模式
        
    Returns:
        dict: 分析结果，包含是否降级信息
    """
    task_id = self.request.id
    
    try:
        # 检查缓存
        if REDIS_AVAILABLE and mode == 'smart':
            cache_key = get_cache_key(text, mode)
            cached = redis_client.get(cache_key)
            if cached:
                result = json.loads(cached)
                result['source'] = 'cache'
                return result
        
        # 执行分析
        from services.sentiment_service import SentimentService
        result = SentimentService.analyze(text, mode)
        result['source'] = 'llm' if mode == 'smart' else 'local'
        
        # 缓存结果
        if REDIS_AVAILABLE and mode == 'smart':
            cache_key = get_cache_key(text, mode)
            redis_client.setex(cache_key, Config.LLM_CACHE_TTL, json.dumps(result))
        
        return result
        
    except Exception as exc:
        logger.error(f"[任务{task_id}] 分析失败，降级到SnowNLP: {exc}")
        
        # 降级到simple模式
        try:
            from services.sentiment_service import SentimentService
            result = SentimentService.analyze(text, 'simple')
            result['source'] = 'fallback'
            result['fallback_reason'] = str(exc)
            return result
        except Exception as e:
            logger.error(f"[任务{task_id}] 降级也失败: {e}")
            raise self.retry(exc=exc)
