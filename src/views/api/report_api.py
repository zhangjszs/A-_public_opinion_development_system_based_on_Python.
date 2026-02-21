#!/usr/bin/env python3
"""
报告生成API路由
功能：PDF/PPT报告生成、下载、模板管理
"""

import logging
import os
import tempfile
from datetime import datetime

from flask import Blueprint, g, jsonify, request, send_file

from utils.api_response import error, ok
from utils.rate_limiter import rate_limit
from utils.report_generator import ReportConfig, report_generator

logger = logging.getLogger(__name__)

bp = Blueprint('report', __name__, url_prefix='/api/report')


def get_demo_report_data():
    """获取演示报告数据"""
    return {
        'summary': {
            'total_articles': 12580,
            'total_comments': 89632,
            'positive_count': 45230,
            'neutral_count': 28450,
            'negative_count': 15952,
        },
        'sentiment_analysis': {
            '正面情感占比': '50.5%',
            '中性情感占比': '31.7%',
            '负面情感占比': '17.8%',
            '情感倾向指数': '0.68',
            '情感波动趋势': '整体稳定，略有上升'
        },
        'hot_topics': [
            {'name': '科技创新', 'heat': 9856},
            {'name': '人工智能', 'heat': 8742},
            {'name': '新能源', 'heat': 7653},
            {'name': '数字经济', 'heat': 6521},
            {'name': '绿色发展', 'heat': 5896},
            {'name': '智慧城市', 'heat': 5234},
            {'name': '乡村振兴', 'heat': 4567},
            {'name': '教育改革', 'heat': 4123},
            {'name': '医疗健康', 'heat': 3890},
            {'name': '文化传承', 'heat': 3456},
        ],
        'alerts': [
            {'level': 'danger', 'title': '负面舆情激增', 'message': '过去30分钟内检测到50条负面评论'},
            {'level': 'warning', 'title': '讨论量异常增长', 'message': '讨论量达到基线的3.5倍'},
            {'level': 'info', 'title': '热点话题出现', 'message': '话题「科技创新」被提及超过100次'},
        ]
    }


@bp.route('/generate', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def generate_report():
    """
    生成报告

    Body:
        format: 报告格式
        title: 报告标题
        data: 报告数据 (可选，不提供则使用演示数据)
    """
    try:
        data = request.json or {}

        format_type = data.get('format', 'pdf').lower()
        title = data.get('title', '舆情分析报告')
        report_data = data.get('data') or get_demo_report_data()

        if format_type not in ['pdf', 'ppt']:
            return error('不支持的报告格式，请选择 pdf 或 ppt', code=400), 400

        template = data.get('template', 'standard')
        sections = data.get('sections', None)

        config = ReportConfig(
            title=title,
            subtitle=f"自动生成于 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            author='微博舆情分析系统',
            template=template,
            sections=sections,
        )

        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format_type == 'pdf':
            output_path = os.path.join(temp_dir, f"report_{timestamp}.pdf")
        else:
            output_path = os.path.join(temp_dir, f"report_{timestamp}.pptx")

        result_path = report_generator.generate_report(
            report_data,
            format=format_type,
            output_path=output_path,
            config=config
        )

        if result_path:
            return ok({
                'file_path': result_path,
                'download_url': f'/api/report/download/{os.path.basename(result_path)}',
                'format': format_type,
                'generated_at': datetime.now().isoformat()
            }, msg='报告生成成功'), 200
        else:
            return error('报告生成失败', code=500), 500

    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        return error('报告生成失败', code=500), 500


@bp.route('/generate-all', methods=['POST'])
@rate_limit(max_requests=3, window_seconds=60)
def generate_all_reports():
    """生成所有格式报告"""
    try:
        data = request.json or {}
        title = data.get('title', '舆情分析报告')
        report_data = data.get('data') or get_demo_report_data()

        config = ReportConfig(
            title=title,
            subtitle=f"自动生成于 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            author='微博舆情分析系统'
        )

        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(temp_dir, f"reports_{timestamp}")

        results = report_generator.generate_all(report_data, output_dir, config)

        if results:
            return ok({
                'files': {
                    fmt: {
                        'file_path': path,
                        'download_url': f'/api/report/download/{os.path.basename(path)}'
                    }
                    for fmt, path in results.items()
                },
                'generated_at': datetime.now().isoformat()
            }, msg='报告生成成功'), 200
        else:
            return error('报告生成失败', code=500), 500

    except Exception as e:
        logger.error(f"批量报告生成失败: {e}")
        return error('报告生成失败', code=500), 500


@bp.route('/download/<filename>', methods=['GET'])
def download_report(filename: str):
    """下载报告文件"""
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        if not os.path.exists(file_path):
            return error('文件不存在', code=404), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        return error('文件下载失败', code=500), 500


@bp.route('/preview/<filename>', methods=['GET'])
def preview_report(filename: str):
    """预览报告文件"""
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)

        if not os.path.exists(file_path):
            return error('文件不存在', code=404), 404

        return send_file(file_path)

    except Exception as e:
        logger.error(f"文件预览失败: {e}")
        return error('文件预览失败', code=500), 500


@bp.route('/templates', methods=['GET'])
def get_templates():
    """获取报告模板列表"""
    templates = [
        {
            'id': 'brief',
            'name': '简报',
            'description': '精简版报告，仅包含核心数据',
            'sections': ['summary', 'sentiment'],
            'chart_slots': ['sentiment_pie'],
        },
        {
            'id': 'standard',
            'name': '标准报告',
            'description': '包含数据概览、情感分析、热门话题、预警记录',
            'sections': ['summary', 'sentiment', 'topics', 'alerts'],
            'chart_slots': ['sentiment_pie', 'topics_bar', 'alert_bar'],
        },
        {
            'id': 'detailed',
            'name': '详细报告',
            'description': '完整版报告，包含所有分析内容',
            'sections': ['summary', 'sentiment', 'topics', 'alerts', 'trend'],
            'chart_slots': ['sentiment_pie', 'topics_bar', 'alert_bar', 'trend_line'],
        },
    ]

    return ok({'templates': templates}), 200


@bp.route('/demo-data', methods=['GET'])
def get_demo_data():
    """获取演示数据"""
    return ok(get_demo_report_data()), 200
