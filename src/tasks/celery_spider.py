#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫异步任务模块
功能：将同步爬虫改造为Celery异步任务，支持进度追踪
"""

import os
import sys
import time
import csv
import logging
from typing import Generator, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery import current_task
from tasks.celery_config import celery_app
from config.settings import Config

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def spider_search_task(self, keyword: str, page_num: int = 3) -> Dict[str, Any]:
    """
    关键词搜索爬虫任务（异步）
    
    Args:
        keyword: 搜索关键词
        page_num: 爬取页数
        
    Returns:
        dict: 任务执行结果
    """
    task_id = self.request.id
    logger.info(f"[任务{task_id}] 开始搜索爬虫: keyword={keyword}, pages={page_num}")
    
    try:
        # 更新任务状态为"开始"
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': page_num,
                'status': '初始化爬虫...',
                'keyword': keyword
            }
        )
        
        # 导入爬虫模块
        from spider.spiderContent import init, get_json, parse_json
        from spider.config import get_config_manager
        
        # 初始化
        init()
        
        # 获取配置
        config = get_config_manager()
        search_url = 'https://weibo.com/ajax/statuses/search'
        
        total_articles = 0
        success_pages = 0
        
        # 逐页爬取
        for page in range(1, page_num + 1):
            try:
                # 更新进度
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': page,
                        'total': page_num,
                        'status': f'正在爬取第 {page}/{page_num} 页',
                        'articles': total_articles,
                        'keyword': keyword
                    }
                )
                
                # 构造搜索参数
                params = {
                    'q': keyword,
                    'type': 'all',
                    'sub': 'all',
                    'timescope': 'custom',
                    'refer': 'g',
                    'page': page,
                    'count': 10
                }
                
                # 发送请求（使用配置管理器的安全请求方法）
                response = config.make_safe_request(
                    search_url,
                    method='GET',
                    params=params,
                    use_proxy=True
                )
                
                if response and response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'list' in data['data']:
                        statuses = data['data']['list']
                        valid_statuses = [s for s in statuses if 'text_raw' in s or 'text' in s]
                        
                        if valid_statuses:
                            parse_json(valid_statuses, f"搜索:{keyword}")
                            total_articles += len(valid_statuses)
                            success_pages += 1
                            logger.info(f"[任务{task_id}] 第{page}页成功: {len(valid_statuses)}条")
                        else:
                            logger.warning(f"[任务{task_id}] 第{page}页无有效数据")
                    else:
                        logger.warning(f"[任务{task_id}] 第{page}页响应格式异常")
                else:
                    logger.error(f"[任务{task_id}] 第{page}页请求失败: {response.status_code if response else 'None'}")
                
            except Exception as e:
                logger.error(f"[任务{task_id}] 第{page}页异常: {e}")
                # 继续下一页，不中断整个任务
                continue
        
        # 任务完成
        result = {
            'status': 'success',
            'task_id': task_id,
            'keyword': keyword,
            'total_pages': page_num,
            'success_pages': success_pages,
            'total_articles': total_articles,
            'completed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"[任务{task_id}] 完成: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"[任务{task_id}] 失败: {exc}")
        # 触发重试
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def spider_comments_task(self, article_limit: int = 50) -> Dict[str, Any]:
    """
    评论爬虫任务（异步）
    爬取articleData.csv中的文章评论
    
    Args:
        article_limit: 限制爬取的文章数量（防止任务过长）
        
    Returns:
        dict: 任务执行结果
    """
    task_id = self.request.id
    logger.info(f"[任务{task_id}] 开始评论爬虫: limit={article_limit}")
    
    try:
        from spider.spiderComments import init, get_json, parse_json
        from spider.config import get_config_manager, DEFAULT_DELAY
        
        init()
        
        url = 'https://weibo.com/ajax/statuses/buildComments'
        article_csv_path = os.path.join(Config.DATA_DIR, 'articleData.csv')
        
        if not os.path.exists(article_csv_path):
            return {
                'status': 'failed',
                'error': f'articleData.csv不存在: {article_csv_path}',
                'task_id': task_id
            }
        
        total_comments = 0
        processed_articles = 0
        
        with open(article_csv_path, 'r', encoding='utf8') as readerFile:
            reader = csv.reader(readerFile)
            try:
                header = next(reader)  # 跳过标题
            except StopIteration:
                return {'status': 'failed', 'error': 'CSV文件为空', 'task_id': task_id}
            
            articles = list(reader)[:article_limit]  # 限制数量
            total = len(articles)
            
            for i, article in enumerate(articles):
                if not article:
                    continue
                
                try:
                    articleId = article[0]
                    
                    # 更新进度
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total,
                            'status': f'正在爬取文章 {articleId} 的评论',
                            'comments': total_comments
                        }
                    )
                    
                    # 从detailUrl提取uid
                    uid = None
                    if len(article) > 9:
                        detail_url = article[9]
                        if detail_url and 'weibo.com' in detail_url:
                            try:
                                parts = detail_url.replace('https://weibo.com/', '').split('/')
                                if len(parts) >= 1:
                                    uid = parts[0]
                            except:
                                pass
                    
                    # 延时
                    import random
                    if isinstance(DEFAULT_DELAY, tuple):
                        time.sleep(random.uniform(DEFAULT_DELAY[0], DEFAULT_DELAY[1]))
                    else:
                        time.sleep(DEFAULT_DELAY)
                    
                    # 获取评论
                    config = get_config_manager()
                    headers = config.get_random_headers()
                    if uid:
                        headers['Referer'] = f'https://weibo.com/{uid}/'
                    
                    params = {
                        'is_reload': '1',
                        'id': articleId,
                        'is_show_bulletin': '2',
                        'is_mix': '0',
                        'count': '10',
                        'uid': uid or 'nouid',
                        'fetch_level': '0',
                        'locale': 'zh-CN'
                    }
                    
                    response = config.make_safe_request(
                        url,
                        method='GET',
                        params=params,
                        use_proxy=True
                    )
                    
                    if response and response.status_code == 200:
                        result = parse_json(response.json(), articleId)
                        if result == "SUCCESS":
                            total_comments += 1
                            processed_articles += 1
                    
                except Exception as e:
                    logger.error(f"[任务{task_id}] 处理文章异常: {e}")
                    continue
        
        return {
            'status': 'success',
            'task_id': task_id,
            'processed_articles': processed_articles,
            'total_comments_pages': total_comments,
            'completed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as exc:
        logger.error(f"[任务{task_id}] 评论爬虫失败: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(bind=True)
def get_task_progress(self, task_id: str) -> Dict[str, Any]:
    """
    查询任务进度
    
    Args:
        task_id: 任务ID
        
    Returns:
        dict: 任务状态和进度信息
    """
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        'task_id': task_id,
        'state': result.state,
    }
    
    if result.state == 'PENDING':
        response['status'] = '任务等待中...'
    elif result.state == 'PROGRESS':
        response['progress'] = result.info
    elif result.state == 'SUCCESS':
        response['result'] = result.result
    elif result.state == 'FAILURE':
        response['error'] = str(result.info)
    
    return response


def search_weibo_generator(keyword: str, page_num: int) -> Generator[Dict, None, None]:
    """
    生成器版本的微博搜索（用于实时进度反馈）
    
    Yields:
        dict: 每页的进度信息
    """
    from spider.spiderContent import init, get_json, parse_json
    from spider.config import get_config_manager
    
    init()
    config = get_config_manager()
    search_url = 'https://weibo.com/ajax/statuses/search'
    
    for page in range(1, page_num + 1):
        params = {
            'q': keyword,
            'type': 'all',
            'sub': 'all',
            'timescope': 'custom',
            'refer': 'g',
            'page': page,
            'count': 10
        }
        
        try:
            response = config.make_safe_request(
                search_url,
                method='GET',
                params=params,
                use_proxy=True
            )
            
            if response and response.status_code == 200:
                data = response.json()
                if 'data' in data and 'list' in data['data']:
                    statuses = data['data']['list']
                    valid_statuses = [s for s in statuses if 'text_raw' in s or 'text' in s]
                    
                    if valid_statuses:
                        parse_json(valid_statuses, f"搜索:{keyword}")
                        yield {
                            'page': page,
                            'count': len(valid_statuses),
                            'status': 'success'
                        }
                    else:
                        yield {'page': page, 'count': 0, 'status': 'no_data'}
                else:
                    yield {'page': page, 'count': 0, 'status': 'invalid_response'}
            else:
                yield {'page': page, 'count': 0, 'status': 'request_failed'}
                
        except Exception as e:
            yield {'page': page, 'count': 0, 'status': 'error', 'error': str(e)}
