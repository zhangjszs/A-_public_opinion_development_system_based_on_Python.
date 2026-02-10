#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理 API
功能：提供爬虫概览、同步爬取、日志查询等接口
"""

import os
import time
import json
import threading
import logging
from datetime import datetime
from flask import Blueprint, request
from config.settings import Config
from utils.api_response import ok, error
from utils.authz import admin_required

logger = logging.getLogger(__name__)

spider_bp = Blueprint('spider_api', __name__, url_prefix='/api/spider')

# 爬虫任务状态（内存存储，进程级别）
_spider_state = {
    'running': False,
    'current_task': None,
    'progress': 0,
    'message': '',
    'history': [],  # 最近的爬取记录
}
_spider_lock = threading.Lock()


def _add_history(action, status, detail='', count=0):
    """添加一条爬取历史记录"""
    record = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': action,
        'status': status,
        'detail': detail,
        'count': count,
    }
    with _spider_lock:
        _spider_state['history'].insert(0, record)
        # 只保留最近 50 条
        _spider_state['history'] = _spider_state['history'][:50]
    return record


@spider_bp.route('/overview', methods=['GET'])
@admin_required
def spider_overview():
    """
    获取爬虫概览数据：文章/评论/用户总数、最近文章时间等
    """
    try:
        from utils.query import querys, query_dataframe

        # 统计各表数量
        article_count = 0
        comment_count = 0
        user_count = 0
        latest_article_time = '暂无数据'
        latest_comment_time = '暂无数据'

        try:
            result = querys('SELECT COUNT(*) as cnt FROM article', [], 'select')
            if result:
                article_count = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get('cnt', 0)
        except Exception:
            pass

        try:
            result = querys('SELECT COUNT(*) as cnt FROM comments', [], 'select')
            if result:
                comment_count = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get('cnt', 0)
        except Exception:
            pass

        try:
            result = querys('SELECT COUNT(*) as cnt FROM user', [], 'select')
            if result:
                user_count = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get('cnt', 0)
        except Exception:
            pass

        try:
            result = querys('SELECT MAX(created_at) as latest FROM article', [], 'select')
            if result and result[0]:
                val = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get('latest', '')
                if val:
                    latest_article_time = str(val)
        except Exception:
            pass

        try:
            result = querys('SELECT MAX(created_at) as latest FROM comments', [], 'select')
            if result and result[0]:
                val = result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get('latest', '')
                if val:
                    latest_comment_time = str(val)
        except Exception:
            pass

        # 获取每日文章数趋势（最近 7 天）
        daily_trend = []
        try:
            df = query_dataframe('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM article
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    daily_trend.append({
                        'date': str(row['date']),
                        'count': int(row['count']),
                    })
        except Exception:
            pass

        # 获取每日评论数趋势
        comment_trend = []
        try:
            df = query_dataframe('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM comments
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    comment_trend.append({
                        'date': str(row['date']),
                        'count': int(row['count']),
                    })
        except Exception:
            pass

        return ok({
            'articleCount': article_count,
            'commentCount': comment_count,
            'userCount': user_count,
            'latestArticleTime': latest_article_time,
            'latestCommentTime': latest_comment_time,
            'isRunning': _spider_state['running'],
            'currentTask': _spider_state['current_task'],
            'progress': _spider_state['progress'],
            'message': _spider_state['message'],
            'dailyTrend': daily_trend,
            'commentTrend': comment_trend,
            'history': _spider_state['history'][:20],
        }), 200

    except Exception as e:
        logger.error(f"获取爬虫概览失败: {e}")
        return error(f'获取概览失败: {e}', code=500), 500


@spider_bp.route('/crawl', methods=['POST'])
@admin_required
def spider_crawl():
    """
    触发同步爬取任务（在后台线程中执行，不依赖 Celery）
    Body:
        type: 'hot' | 'search' | 'comments'
        keyword: 搜索关键词（type=search 时必填）
        pageNum: 爬取页数（默认 3）
    """
    with _spider_lock:
        if _spider_state['running']:
            return ok(
                {
                    'currentTask': _spider_state['current_task'],
                    'progress': _spider_state['progress'],
                },
                msg='已有爬虫任务正在运行，请等待完成',
                code=409
            ), 409

    data = request.json or {}
    crawl_type = data.get('type', 'hot')
    keyword = data.get('keyword', '')
    page_num = min(int(data.get('pageNum', 3)), 10)

    # 参数校验
    if crawl_type == 'search' and not keyword.strip():
        return error('关键词搜索模式下 keyword 不能为空', code=400), 400

    # 在后台线程执行爬取
    def run_crawl():
        try:
            with _spider_lock:
                _spider_state['running'] = True
                _spider_state['progress'] = 0

            if crawl_type == 'hot':
                _spider_state['current_task'] = '刷新热门微博'
                _spider_state['message'] = '正在爬取热门微博...'
                count = _crawl_hot(page_num)
                _add_history('刷新热门微博', 'success', f'爬取 {page_num} 页', count)

            elif crawl_type == 'search':
                _spider_state['current_task'] = f'搜索: {keyword}'
                _spider_state['message'] = f'正在搜索 "{keyword}"...'
                count = _crawl_search(keyword, page_num)
                _add_history(f'关键词搜索: {keyword}', 'success', f'爬取 {page_num} 页', count)

            elif crawl_type == 'comments':
                _spider_state['current_task'] = '爬取评论'
                _spider_state['message'] = '正在爬取评论数据...'
                count = _crawl_comments()
                _add_history('爬取评论', 'success', '', count)

            _spider_state['message'] = '爬取完成'
            _spider_state['progress'] = 100

        except Exception as e:
            logger.error(f"爬虫任务失败: {e}")
            _spider_state['message'] = f'爬取失败: {e}'
            _add_history(
                _spider_state['current_task'] or crawl_type,
                'error',
                str(e),
            )
        finally:
            with _spider_lock:
                _spider_state['running'] = False
                _spider_state['current_task'] = None
                _spider_state['progress'] = 0

    thread = threading.Thread(target=run_crawl, daemon=True)
    thread.start()

    task_label = {
        'hot': '刷新热门微博',
        'search': f'搜索: {keyword}',
        'comments': '爬取评论',
    }.get(crawl_type, crawl_type)

    return ok(
        {'type': crawl_type, 'keyword': keyword, 'pageNum': page_num},
        msg=f'爬虫任务已启动: {task_label}'
    ), 200


@spider_bp.route('/logs', methods=['GET'])
@admin_required
def spider_logs():
    """获取爬虫运行日志（读取日志文件最近 N 行）"""
    lines_num = min(int(request.args.get('lines', 100)), 500)

    log_paths = [
        os.path.join(Config.LOG_DIR, 'app.log'),
        os.path.join(Config.BASE_DIR, 'spider', 'weibo_spider.log'),
    ]

    log_lines = []
    for lp in log_paths:
        if os.path.exists(lp):
            try:
                with open(lp, 'r', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()
                    # 取最后 lines_num 行
                    tail = all_lines[-lines_num:]
                    for line in tail:
                        line = line.strip()
                        if line:
                            log_lines.append(line)
            except Exception as e:
                log_lines.append(f'[读取日志失败: {lp}] {e}')

    # 按时间倒序（最新在前）
    log_lines.reverse()

    return ok({'logs': log_lines[:lines_num], 'total': len(log_lines)}), 200


@spider_bp.route('/status', methods=['GET'])
@admin_required
def spider_status():
    """获取当前爬虫运行状态"""
    return ok({
        'isRunning': _spider_state['running'],
        'currentTask': _spider_state['current_task'],
        'progress': _spider_state['progress'],
        'message': _spider_state['message'],
    }), 200


# ========== 爬取实现函数 ==========

def _crawl_hot(page_num=3):
    """同步爬取热门微博并导入数据库"""
    import requests as req
    import random
    from utils.query import querys

    cookie = os.getenv('WEIBO_COOKIE', '')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie,
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://weibo.com/',
    }

    articles = []
    for page in range(page_num):
        _spider_state['progress'] = int((page / page_num) * 80)
        _spider_state['message'] = f'正在爬取第 {page + 1}/{page_num} 页...'

        url = 'https://weibo.com/ajax/feed/hottimeline'
        params = {'group_id': 102803, 'max_id': 0, 'count': 20, 'refresh_type': 1}

        try:
            response = req.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if 'statuses' in result:
                    for item in result['statuses']:
                        user = item.get('user', {}) or {}
                        articles.append({
                            'id': item.get('id', ''),
                            'likeNum': item.get('attitudes_count', 0),
                            'commentsLen': item.get('comments_count', 0),
                            'reposts_count': item.get('reposts_count', 0),
                            'region': (item.get('region_name', '') or '无').replace('发布于 ', '')[:50],
                            'content': item.get('text_raw', '')[:2000],
                            'contentLen': item.get('textLength', 0),
                            'created_at': datetime.now().strftime('%Y-%m-%d'),
                            'type': '热门',
                            'detailUrl': f"https://weibo.com/{user.get('id', '')}/{item.get('mblogid', '')}",
                            'authorAvatar': user.get('avatar_large', '')[:500],
                            'authorName': user.get('screen_name', '')[:100],
                            'authorDetail': f"https://weibo.com/u/{user.get('id', '')}",
                            'isVip': user.get('v_plus', 0),
                        })
        except Exception as e:
            logger.warning(f"爬取第{page + 1}页失败: {e}")
        time.sleep(random.uniform(0.5, 1))

    _spider_state['progress'] = 85
    _spider_state['message'] = '正在导入数据库...'

    imported = 0
    for a in articles:
        try:
            sql = """INSERT INTO article
                (id, likeNum, commentsLen, reposts_count, region, content,
                 contentLen, created_at, type, detailUrl, authorAvatar,
                 authorName, authorDetail, isVip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                likeNum=VALUES(likeNum), commentsLen=VALUES(commentsLen)"""
            querys(sql, [
                a['id'], a['likeNum'], a['commentsLen'], a['reposts_count'],
                a['region'], a['content'], a['contentLen'], a['created_at'],
                a['type'], a['detailUrl'], a['authorAvatar'], a['authorName'],
                a['authorDetail'], a['isVip']
            ])
            imported += 1
        except Exception as e:
            logger.warning(f"导入文章失败: {e}")

    # 清除缓存
    try:
        from utils.cache import clear_cache
        clear_cache()
    except Exception:
        pass

    logger.info(f"热门微博刷新完成: 爬取{len(articles)}条, 导入{imported}条")
    return imported


def _crawl_search(keyword, page_num=3):
    """同步关键词搜索爬取"""
    import requests as req
    import random
    from utils.query import querys

    cookie = os.getenv('WEIBO_COOKIE', '')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie,
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://weibo.com/',
    }

    articles = []
    for page in range(1, page_num + 1):
        _spider_state['progress'] = int((page / page_num) * 80)
        _spider_state['message'] = f'正在搜索 "{keyword}" 第 {page}/{page_num} 页...'

        url = 'https://weibo.com/ajax/side/hotSearch'
        # 搜索 API
        search_url = f'https://weibo.com/ajax/statuses/searchResult'
        params = {'q': keyword, 'page': page, 'count': 20}

        try:
            response = req.get(search_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                result = response.json()
                statuses = result.get('data', {}).get('statuses', []) if isinstance(result.get('data'), dict) else []
                for item in statuses:
                    user = item.get('user', {}) or {}
                    articles.append({
                        'id': item.get('id', ''),
                        'likeNum': item.get('attitudes_count', 0),
                        'commentsLen': item.get('comments_count', 0),
                        'reposts_count': item.get('reposts_count', 0),
                        'region': (item.get('region_name', '') or '无').replace('发布于 ', '')[:50],
                        'content': item.get('text_raw', '')[:2000],
                        'contentLen': item.get('textLength', 0),
                        'created_at': datetime.now().strftime('%Y-%m-%d'),
                        'type': f'搜索:{keyword}',
                        'detailUrl': f"https://weibo.com/{user.get('id', '')}/{item.get('mblogid', '')}",
                        'authorAvatar': user.get('avatar_large', '')[:500],
                        'authorName': user.get('screen_name', '')[:100],
                        'authorDetail': f"https://weibo.com/u/{user.get('id', '')}",
                        'isVip': user.get('v_plus', 0),
                    })
        except Exception as e:
            logger.warning(f"搜索第{page}页失败: {e}")
        time.sleep(random.uniform(1, 2))

    _spider_state['progress'] = 85
    _spider_state['message'] = '正在导入数据库...'

    imported = 0
    for a in articles:
        try:
            sql = """INSERT INTO article
                (id, likeNum, commentsLen, reposts_count, region, content,
                 contentLen, created_at, type, detailUrl, authorAvatar,
                 authorName, authorDetail, isVip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                likeNum=VALUES(likeNum), commentsLen=VALUES(commentsLen)"""
            querys(sql, [
                a['id'], a['likeNum'], a['commentsLen'], a['reposts_count'],
                a['region'], a['content'], a['contentLen'], a['created_at'],
                a['type'], a['detailUrl'], a['authorAvatar'], a['authorName'],
                a['authorDetail'], a['isVip']
            ])
            imported += 1
        except Exception as e:
            logger.warning(f"导入搜索文章失败: {e}")

    try:
        from utils.cache import clear_cache
        clear_cache()
    except Exception:
        pass

    logger.info(f"关键词搜索完成 [{keyword}]: 爬取{len(articles)}条, 导入{imported}条")
    return imported


def _crawl_comments():
    """同步爬取评论"""
    _spider_state['progress'] = 10
    _spider_state['message'] = '正在获取待爬取文章列表...'

    try:
        from utils.query import querys
        # 获取最近的文章 ID
        articles = querys(
            'SELECT id FROM article ORDER BY created_at DESC LIMIT 20',
            [], 'select'
        )
        if not articles:
            logger.warning("没有文章可爬取评论")
            return 0

        import requests as req
        import random

        cookie = os.getenv('WEIBO_COOKIE', '')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': cookie,
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://weibo.com/',
        }

        total_imported = 0
        for idx, article in enumerate(articles):
            aid = article[0] if isinstance(article, (list, tuple)) else article.get('id', '')
            _spider_state['progress'] = int(10 + (idx / len(articles)) * 70)
            _spider_state['message'] = f'正在爬取文章 {idx + 1}/{len(articles)} 的评论...'

            url = f'https://weibo.com/ajax/statuses/buildComments'
            params = {'id': aid, 'is_show_bulletin': 2, 'count': 20}

            try:
                response = req.get(url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    comments = result.get('data', []) if isinstance(result.get('data'), list) else []
                    for c in comments:
                        c_user = c.get('user', {}) or {}
                        try:
                            sql = """INSERT IGNORE INTO comments
                                (articleId, created_at, like_counts, region, content,
                                 authorName, authorGender, authorAddress, authorAvatar)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                            querys(sql, [
                                str(aid),
                                c.get('created_at', '')[:50],
                                c.get('like_counts', 0),
                                (c.get('source', '') or '无')[:50],
                                (c.get('text_raw', '') or '')[:2000],
                                c_user.get('screen_name', '')[:100],
                                c_user.get('gender', 'unknown')[:10],
                                (c_user.get('location', '') or '')[:200],
                                c_user.get('avatar_large', '')[:500],
                            ])
                            total_imported += 1
                        except Exception as e:
                            logger.warning(f"导入评论失败: {e}")
            except Exception as e:
                logger.warning(f"爬取文章 {aid} 评论失败: {e}")

            time.sleep(random.uniform(0.5, 1.5))

        try:
            from utils.cache import clear_cache
            clear_cache()
        except Exception:
            pass

        logger.info(f"评论爬取完成: 导入{total_imported}条")
        return total_imported

    except Exception as e:
        logger.error(f"评论爬取失败: {e}")
        raise
