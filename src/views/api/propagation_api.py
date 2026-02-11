#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
传播路径分析API路由
功能：转发链路追踪、传播可视化、KOL影响力分析
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
import logging
import random

from utils.api_response import ok, error
from utils.rate_limiter import rate_limit
from services.propagation_analyzer import PropagationAnalyzer, PropagationNode

logger = logging.getLogger(__name__)

bp = Blueprint('propagation', __name__, url_prefix='/api/propagation')


def generate_demo_data(article_id: str, count: int = 100):
    """生成演示数据"""
    nodes = []
    
    users = [
        ('user_001', '科技观察家', True),
        ('user_002', '互联网分析师', True),
        ('user_003', '微博大V', True),
        ('user_004', '普通用户A', False),
        ('user_005', '普通用户B', False),
        ('user_006', '媒体账号', True),
        ('user_007', '行业专家', True),
        ('user_008', '热心网友', False),
        ('user_009', '资讯博主', True),
        ('user_010', '路人甲', False),
    ]
    
    base_time = datetime.now() - timedelta(hours=24)
    
    origin_node = {
        'id': f'{article_id}_origin',
        'user_id': users[0][0],
        'user_name': users[0][1],
        'content': '这是一条原始微博内容，讨论了最新的科技动态...',
        'post_time': base_time,
        'repost_count': random.randint(500, 2000),
        'comment_count': random.randint(100, 500),
        'like_count': random.randint(1000, 5000),
        'depth': 0,
        'parent_id': None
    }
    nodes.append(origin_node)
    
    for i in range(1, count):
        user = users[i % len(users)]
        parent_idx = random.randint(0, max(0, i - 1))
        parent = nodes[parent_idx]
        
        depth = parent['depth'] + 1 if depth < 5 else 5
        
        node = {
            'id': f'{article_id}_repost_{i}',
            'user_id': user[0],
            'user_name': user[1],
            'content': f'转发微博，发表了自己的看法... #{i}',
            'post_time': base_time + timedelta(minutes=random.randint(1, 1440)),
            'repost_count': random.randint(0, 500) if user[2] else random.randint(0, 50),
            'comment_count': random.randint(0, 200) if user[2] else random.randint(0, 20),
            'like_count': random.randint(0, 1000) if user[2] else random.randint(0, 100),
            'depth': min(depth, 5),
            'parent_id': parent['id']
        }
        nodes.append(node)
    
    return nodes


@bp.route('/analyze/<article_id>', methods=['GET'])
def analyze_propagation(article_id: str):
    """
    分析文章传播路径
    
    Args:
        article_id: 文章ID
    """
    try:
        analyzer = PropagationAnalyzer()
        
        demo_mode = request.args.get('demo', 'true').lower() == 'true'
        node_count = request.args.get('count', 100, type=int)
        
        if demo_mode:
            reposts = generate_demo_data(article_id, node_count)
        else:
            from database import db_session
            sql = """
                SELECT 
                    r.id,
                    r.user_id,
                    u.username as user_name,
                    r.content,
                    r.created_at as post_time,
                    r.repost_count,
                    r.comment_count,
                    r.like_count,
                    r.depth,
                    r.parent_id
                FROM reposts r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.article_id = %s
                ORDER BY r.created_at ASC
            """
            result = db_session.execute(sql, (article_id,))
            reposts = [dict(row) for row in result]
            
            if not reposts:
                reposts = generate_demo_data(article_id, 50)
        
        node_count = analyzer.build_from_reposts(reposts)
        
        summary = analyzer.get_summary()
        
        return ok({
            'article_id': article_id,
            'node_count': node_count,
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"传播路径分析失败: {e}")
        return error('传播路径分析失败', code=500), 500


@bp.route('/graph/<article_id>', methods=['GET'])
def get_propagation_graph(article_id: str):
    """获取传播图数据（用于可视化）"""
    try:
        analyzer = PropagationAnalyzer()
        
        demo_mode = request.args.get('demo', 'true').lower() == 'true'
        node_count = request.args.get('count', 80, type=int)
        
        if demo_mode:
            reposts = generate_demo_data(article_id, node_count)
        else:
            reposts = generate_demo_data(article_id, 50)
        
        analyzer.build_from_reposts(reposts)
        graph_data = analyzer.get_graph_data()
        
        return ok(graph_data), 200
        
    except Exception as e:
        logger.error(f"获取传播图失败: {e}")
        return error('获取传播图失败', code=500), 500


@bp.route('/kol/<article_id>', methods=['GET'])
def get_kol_analysis(article_id: str):
    """获取KOL影响力分析"""
    try:
        analyzer = PropagationAnalyzer()
        
        demo_mode = request.args.get('demo', 'true').lower() == 'true'
        
        if demo_mode:
            reposts = generate_demo_data(article_id, 100)
        else:
            reposts = generate_demo_data(article_id, 50)
        
        analyzer.build_from_reposts(reposts)
        
        kol_nodes = analyzer.get_kol_nodes()
        user_ranking = analyzer.get_user_influence_ranking(20)
        
        return ok({
            'article_id': article_id,
            'kol_count': len(kol_nodes),
            'kol_nodes': [n.to_dict() for n in kol_nodes],
            'user_ranking': user_ranking
        }), 200
        
    except Exception as e:
        logger.error(f"KOL分析失败: {e}")
        return error('KOL分析失败', code=500), 500


@bp.route('/timeline/<article_id>', methods=['GET'])
def get_propagation_timeline(article_id: str):
    """获取传播时间线"""
    try:
        analyzer = PropagationAnalyzer()
        
        interval = request.args.get('interval', 60, type=int)
        
        reposts = generate_demo_data(article_id, 100)
        analyzer.build_from_reposts(reposts)
        
        time_dist = analyzer.get_time_distribution(interval)
        
        return ok({
            'article_id': article_id,
            'interval_minutes': interval,
            'timeline': time_dist
        }), 200
        
    except Exception as e:
        logger.error(f"获取传播时间线失败: {e}")
        return error('获取传播时间线失败', code=500), 500


@bp.route('/depth/<article_id>', methods=['GET'])
def get_depth_distribution(article_id: str):
    """获取传播深度分布"""
    try:
        analyzer = PropagationAnalyzer()
        
        reposts = generate_demo_data(article_id, 100)
        analyzer.build_from_reposts(reposts)
        
        depth_dist = analyzer.get_depth_distribution()
        
        return ok({
            'article_id': article_id,
            'depth_distribution': depth_dist,
            'max_depth': max(depth_dist.keys()) if depth_dist else 0
        }), 200
        
    except Exception as e:
        logger.error(f"获取深度分布失败: {e}")
        return error('获取深度分布失败', code=500), 500


@bp.route('/compare', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def compare_propagation():
    """对比多条传播路径"""
    try:
        data = request.json
        article_ids = data.get('article_ids', [])
        
        if not article_ids or len(article_ids) < 2:
            return error('请提供至少2个文章ID', code=400), 400
        
        if len(article_ids) > 5:
            return error('最多对比5条传播路径', code=400), 400
        
        results = []
        
        for aid in article_ids:
            analyzer = PropagationAnalyzer()
            reposts = generate_demo_data(aid, random.randint(50, 150))
            analyzer.build_from_reposts(reposts)
            
            path = analyzer.analyze_propagation_path()
            results.append({
                'article_id': aid,
                'total_nodes': path.total_nodes,
                'total_depth': path.total_depth,
                'total_reposts': path.total_reposts,
                'propagation_speed': path.propagation_speed,
                'kol_count': len(analyzer.get_kol_nodes())
            })
        
        return ok({
            'comparison': results
        }), 200
        
    except Exception as e:
        logger.error(f"传播路径对比失败: {e}")
        return error('传播路径对比失败', code=500), 500
