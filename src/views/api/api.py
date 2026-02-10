#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
功能：提供RESTful API接口
特性：分页查询、情感分析、参数验证
作者：微博舆情分析系统
"""

from flask import Blueprint, jsonify, request
from services.article_service import ArticleService
from services.auth_service import AuthService
from services.comment_service import CommentService
from services.sentiment_service import SentimentService
from utils.input_validator import validate_password, validate_username, sanitize_input
from utils.log_sanitizer import SafeLogger
from utils.api_response import ok, error
from config.settings import Config
import logging

logger = SafeLogger('api', logging.INFO)
article_service = ArticleService()
auth_service = AuthService()
comment_service = CommentService()

# 创建API蓝图
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        username_raw = (data.get('username') or '').strip()
        password_raw = (data.get('password') or '').strip()

        username_validation = validate_username(username_raw)
        if not username_validation['valid']:
            return error(username_validation['message'], code=400), 400

        password_validation = validate_password(password_raw)
        if not password_validation['valid']:
            return error(password_validation['message'], code=400), 400

        username = sanitize_input(username_raw, max_length=20)
        success, msg, payload = auth_service.login(username, password_raw)
        if success:
            return ok(payload, msg=msg), 200
        return error(msg, code=401), 401
    except Exception as e:
        logger.error(f"API登录异常: {e}")
        return error('服务器内部错误', code=500), 500

@bp.route('/auth/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json(silent=True) or {}
        username_raw = (data.get('username') or '').strip()
        password_raw = (data.get('password') or '').strip()
        confirm_raw = (data.get('confirmPassword') or data.get('passwordCheked') or '').strip()

        username_validation = validate_username(username_raw)
        if not username_validation['valid']:
            return error(username_validation['message'], code=400), 400

        password_validation = validate_password(password_raw)
        if not password_validation['valid']:
            return error(password_validation['message'], code=400), 400

        username = sanitize_input(username_raw, max_length=20)
        success, msg = auth_service.register(username, password_raw, confirm_raw)
        if success:
            return ok(msg=msg), 200
        return error(msg, code=400), 400
    except Exception as e:
        logger.error(f"API注册异常: {e}")
        return error('服务器内部错误', code=500), 500

@bp.route('/auth/me', methods=['GET'])
def api_me():
    user = getattr(request, 'current_user', None)
    if not user:
        return error('未认证', code=401), 401
    try:
        from utils.query import querys
        users = querys(
            'SELECT id, username, createTime FROM user WHERE id = %s',
            [user['user_id']],
            'select'
        )
        if not users:
            return error('用户不存在', code=404), 404
        info = users[0]
        return ok({
            'id': info.get('id'),
            'username': info.get('username'),
            'createTime': str(info.get('createTime', '')),
            'is_admin': bool(Config.ADMIN_USERS and info.get('username') in Config.ADMIN_USERS),
        }), 200
    except Exception as e:
        logger.error(f"获取当前用户信息异常: {e}")
        return error('服务器内部错误', code=500), 500

@bp.route('/auth/logout', methods=['POST'])
def api_logout():
    return ok(), 200

@bp.route('/stats/summary', methods=['GET'])
def get_stats_summary():
    """获取系统统计概览"""
    try:
        data = article_service.get_stats_summary()
        return ok(data), 200
    except Exception as e:
        return error(str(e), code=500), 500

@bp.route('/articles', methods=['GET'])
def get_articles():
    """
    获取文章列表（支持分页、关键词搜索、时间筛选）
    Params:
        page: 页码 (默认1)
        limit: 每页数量 (默认10)
        keyword: 搜索关键词
        start_time: 开始时间
        end_time: 结束时间
    """
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 100)  # 限制最大100条
        keyword = request.args.get('keyword', '')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        article_type = request.args.get('type', '')
        region = request.args.get('region', '')
        
        # 参数校验：关键词长度和SQL注入检测
        if keyword or article_type or region:
            from utils.input_validator import validate_keyword, detect_sql_injection
            if keyword:
                validation = validate_keyword(keyword)
                if not validation['valid']:
                    return error(validation['message'], code=400), 400
                if detect_sql_injection(keyword):
                    logger.warning(f"检测到SQL注入尝试: keyword={keyword[:50]}")
                    return error('关键词包含非法字符', code=400), 400

            if article_type:
                validation = validate_keyword(article_type)
                if not validation['valid']:
                    return error(validation['message'], code=400), 400
                if detect_sql_injection(article_type):
                    logger.warning(f"检测到SQL注入尝试: type={article_type[:50]}")
                    return error('类型包含非法字符', code=400), 400

            if region:
                validation = validate_keyword(region)
                if not validation['valid']:
                    return error(validation['message'], code=400), 400
                if detect_sql_injection(region):
                    logger.warning(f"检测到SQL注入尝试: region={region[:50]}")
                    return error('地区包含非法字符', code=400), 400
        
        # 参数校验：时间格式
        if start_time or end_time:
            import re
            time_pattern = r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$'
            if start_time and not re.match(time_pattern, start_time):
                return error('开始时间格式错误（应为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）', code=400), 400
            if end_time and not re.match(time_pattern, end_time):
                return error('结束时间格式错误（应为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）', code=400), 400
        
        result = article_service.get_articles(page, limit, keyword, start_time, end_time, article_type, region)
                
        return ok(result), 200
        
    except Exception as e:
        return error(str(e), code=500), 500

@bp.route('/comments', methods=['GET'])
def get_comments():
    """
    获取评论列表（支持分页、关键词搜索、时间筛选）
    Params:
        page: 页码 (默认1)
        limit: 每页数量 (默认10)
        keyword: 搜索关键词（评论内容）
        article_id: 文章ID（rootId）
        user: 评论用户名（模糊匹配）
        start_time: 开始时间
        end_time: 结束时间
    """
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 10)), 100)
        keyword = request.args.get('keyword', '')
        article_id = request.args.get('article_id', '')
        user = request.args.get('user', '')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')

        if keyword or user:
            from utils.input_validator import validate_keyword, detect_sql_injection

            if keyword:
                validation = validate_keyword(keyword)
                if not validation['valid']:
                    return error(validation['message'], code=400), 400
                if detect_sql_injection(keyword):
                    logger.warning(f"检测到SQL注入尝试: keyword={keyword[:50]}")
                    return error('关键词包含非法字符', code=400), 400

            if user:
                validation = validate_keyword(user)
                if not validation['valid']:
                    return error(validation['message'], code=400), 400
                if detect_sql_injection(user):
                    logger.warning(f"检测到SQL注入尝试: user={user[:50]}")
                    return error('用户名包含非法字符', code=400), 400

        if start_time or end_time:
            import re

            time_pattern = r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$'
            if start_time and not re.match(time_pattern, start_time):
                return error('开始时间格式错误（应为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）', code=400), 400
            if end_time and not re.match(time_pattern, end_time):
                return error('结束时间格式错误（应为YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）', code=400), 400

        result = comment_service.get_comments(page, limit, keyword, article_id, user, start_time, end_time)
        return ok(result), 200
    except Exception as e:
        return error(str(e), code=500), 500

@bp.route('/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """
    文本情感分析接口
    Body:
        text: 待分析文本
        mode: 分析模式 (simple/smart)，默认 simple
        async: 是否异步执行（默认false）
    """
    try:
        data = request.json
        text = data.get('text', '')
        mode = data.get('mode', 'simple')
        is_async = data.get('async', False)
        
        if not text:
            return error('text is required', code=400), 400
        
        # 参数校验
        from utils.input_validator import validate_keyword
        validation = validate_keyword(text[:50])  # 只校验前50字符
        if not validation['valid']:
            return error(validation['message'], code=400), 400
        
        # 异步模式
        if is_async:
            from tasks.celery_sentiment import analyze_single_with_fallback
            task = analyze_single_with_fallback.delay(text, mode)
            return ok({
                'task_id': task.id,
                'status': 'PENDING',
                'check_url': f'/api/tasks/{task.id}/status'
            }, msg='任务已提交', code=202), 202
        
        # 同步模式
        result = SentimentService.analyze(text, mode)
            
        return ok(result), 200
        
    except Exception as e:
        logger.error(f"情感分析接口异常: {e}")
        return error('服务器内部错误', code=500), 500


@bp.route('/spider/search', methods=['POST'])
def spider_search():
    """
    触发关键词搜索爬虫（异步）
    Body:
        keyword: 搜索关键词
        page_num: 爬取页数（默认3页）
    """
    try:
        data = request.json
        keyword = data.get('keyword', '')
        page_num = min(int(data.get('page_num', 3)), 10)  # 最多10页，防止滥用
        
        # 参数校验
        from utils.input_validator import validate_keyword
        validation = validate_keyword(keyword)
        if not validation['valid']:
            return error(validation['message'], code=400), 400
        
        # 提交异步任务
        from tasks.celery_spider import spider_search_task
        task = spider_search_task.delay(keyword, page_num)
        
        logger.info(f"爬虫任务已提交: task_id={task.id}, keyword={keyword}")
        
        return ok({
            'task_id': task.id,
            'keyword': keyword,
            'page_num': page_num,
            'status': 'PENDING',
            'check_url': f'/api/tasks/{task.id}/status'
        }, msg='爬虫任务已提交', code=202), 202
        
    except Exception as e:
        logger.error(f"爬虫接口异常: {e}")
        return error('服务器内部错误', code=500), 500


@bp.route('/spider/comments', methods=['POST'])
def spider_comments():
    """
    触发评论爬虫（异步）
    Body:
        article_limit: 限制爬取的文章数量（默认50）
    """
    try:
        data = request.json or {}
        article_limit = min(int(data.get('article_limit', 50)), 100)  # 最多100篇
        
        # 提交异步任务
        from tasks.celery_spider import spider_comments_task
        task = spider_comments_task.delay(article_limit)
        
        logger.info(f"评论爬虫任务已提交: task_id={task.id}, limit={article_limit}")
        
        return ok({
            'task_id': task.id,
            'article_limit': article_limit,
            'status': 'PENDING',
            'check_url': f'/api/tasks/{task.id}/status'
        }, msg='评论爬虫任务已提交', code=202), 202
        
    except Exception as e:
        logger.error(f"评论爬虫接口异常: {e}")
        return error('服务器内部错误', code=500), 500


@bp.route('/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """
    查询异步任务状态
    """
    try:
        from tasks.celery_spider import get_task_progress
        result = get_task_progress(task_id)
        
        return ok(result), 200
        
    except Exception as e:
        logger.error(f"查询任务状态异常: {e}")
        return error('查询失败', code=500), 500


@bp.route('/spider/refresh', methods=['POST'])
def refresh_data():
    """
    同步刷新热门微博数据
    直接爬取最新热门微博并更新数据库
    Body:
        page_num: 爬取页数（默认3页）
    """
    try:
        user = getattr(request, 'current_user', None)
        if Config.ADMIN_USERS and (not user or user.get('username') not in Config.ADMIN_USERS):
            return error('权限不足', code=403), 403
        # 这里的逻辑也应该移到 ArticleService 或 SpiderService
        # 为了演示，我们假设 ArticleService 暂时处理不了复杂的爬虫逻辑
        # 或者我们可以创建一个 SpiderService
        import requests
        import os
        import time
        import random
        from datetime import datetime
        from utils.query import querys
        
        data = request.json or {}
        page_num = min(int(data.get('page_num', 3)), 5)  # 最多5页
        
        # 获取Cookie
        cookie = os.getenv('WEIBO_COOKIE', '')
        if not cookie:
            return error('WEIBO_COOKIE未配置', code=400), 400
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': cookie,
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://weibo.com/',
        }
        
        articles = []
        
        for page in range(page_num):
            url = 'https://weibo.com/ajax/feed/hottimeline'
            params = {
                'group_id': 102803,
                'max_id': 0,
                'count': 20,
                'refresh_type': 1
            }
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
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
                logger.warning(f"爬取第{page+1}页失败: {e}")
                continue
            
            time.sleep(random.uniform(0.5, 1))
        
        # 导入到数据库
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
        except:
            pass
        
        logger.info(f"刷新数据完成: 爬取{len(articles)}条, 导入{imported}条")
        
        return ok({
            'crawled': len(articles),
            'imported': imported,
            'pages': page_num
        }, msg='刷新成功'), 200
        
    except Exception as e:
        logger.error(f"刷新数据异常: {e}")
        return error(str(e), code=500), 500


@bp.route('/stats/today', methods=['GET'])
def get_today_stats():
    """获取今日数据统计"""
    try:
        # TODO: Move to ArticleService or StatsService
        from datetime import date
        from utils.query import querys
        today = date.today().strftime('%Y-%m-%d')
        
        # 今日文章数
        today_articles = querys(
            "SELECT count(*) as count FROM article WHERE created_at = %s", 
            [today],
            type='select'
        )[0]['count']
        
        # 今日评论数
        today_comments = querys(
            "SELECT count(*) as count FROM comments WHERE DATE(created_at) = %s",
            [today],
            type='select'
        )[0]['count']
        
        # 最新更新时间
        latest = querys(
            "SELECT MAX(created_at) as latest FROM article",
            [],
            'select'
        )[0]['latest']
        
        return ok({
            'today_articles': today_articles,
            'today_comments': today_comments,
            'latest_update': str(latest) if latest else None
        }), 200
    except Exception as e:
        logger.error(f"获取今日统计失败: {e}")
        return error(str(e), code=500), 500
