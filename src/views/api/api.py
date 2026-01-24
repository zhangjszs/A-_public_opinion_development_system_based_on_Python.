#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
功能：提供RESTful API接口
特性：分页查询、情感分析、参数验证
作者：微博舆情分析系统
"""

from flask import Blueprint, jsonify, request
from utils.query import query_dataframe, querys
from snownlp import SnowNLP
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 创建API蓝图
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/stats/summary', methods=['GET'])
def get_stats_summary():
    """获取系统统计概览"""
    try:
        # 获取各表总数
        article_count = querys('SELECT count(*) as count FROM article')[0]['count']
        comment_count = querys('SELECT count(*) as count FROM comments')[0]['count']
        user_count = querys('SELECT count(*) as count FROM user')[0]['count']
        
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'articles': article_count,
                'comments': comment_count,
                'users': user_count
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500

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
        limit = int(request.args.get('limit', 10))
        keyword = request.args.get('keyword', '')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        offset = (page - 1) * limit
        params = []
        sql = "SELECT * FROM article WHERE 1=1"
        count_sql = "SELECT count(*) as count FROM article WHERE 1=1"
        
        if keyword:
            sql += " AND content LIKE %s"
            count_sql += " AND content LIKE %s"
            params.append(f"%{keyword}%")
            
        if start_time and end_time:
            sql += " AND created_at BETWEEN %s AND %s"
            count_sql += " AND created_at BETWEEN %s AND %s"
            params.append(start_time)
            params.append(end_time)
            
        # 获取总数
        total = querys(count_sql, params)[0]['count']
        
        # 获取分页数据
        sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.append(limit)
        params.append(offset)
        
        # 使用querys而不直接用DataFrame，以便于返回JSON
        articles = querys(sql, params, 'select')
        
        # 简单处理日期格式
        for item in articles:
            if 'created_at' in item and item['created_at']:
                item['created_at'] = str(item['created_at'])
                
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'total': total,
                'page': page,
                'limit': limit,
                'list': articles
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)}), 500

@bp.route('/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """
    文本情感分析接口
    Body:
        text: 待分析文本
        mode: 分析模式 (simple/smart)，默认 simple
    """
    try:
        data = request.json
        text = data.get('text', '')
        mode = data.get('mode', 'simple')
        
        if not text:
            return jsonify({'code': 400, 'msg': 'text is required'}), 400
            
        from services.sentiment_service import SentimentService
        result = SentimentService.analyze(text, mode)
            
        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': result
        })
        
    except Exception as e:
         return jsonify({'code': 500, 'msg': str(e)}), 500
