#!/usr/bin/env python3
"""
微博舆情分析系统 - Celery异步任务配置
功能：配置Celery应用，定义任务队列和调度
"""

import logging
import time

from celery import Celery
from celery.signals import task_failure, task_prerun, task_success

from config.settings import Config

logger = logging.getLogger(__name__)

# 创建Celery应用实例
celery_app = Celery(
    'weibo_sentiment',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=[
        'tasks.celery_spider',  # 爬虫任务模块
        'tasks.celery_sentiment',  # 情感分析任务模块
    ]
)

# Celery配置
celery_app.conf.update(
    # 序列化配置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # 时区配置
    timezone='Asia/Shanghai',
    enable_utc=True,

    # 任务执行配置
    task_track_started=True,  # 追踪任务开始状态
    task_time_limit=3600,  # 任务硬限制：1小时
    task_soft_time_limit=3300,  # 软限制：55分钟（提前警告）
    worker_prefetch_multiplier=1,  # 避免任务积压，每个worker只预取1个任务
    worker_max_tasks_per_child=1000,  # 每个worker进程处理1000个任务后重启（防止内存泄漏）

    # 结果后端配置
    result_expires=3600 * 24,  # 结果保存24小时
    result_extended=True,  # 保存更多任务元数据

    # 重试配置
    task_default_retry_delay=60,  # 默认重试间隔60秒
    task_max_retries=3,  # 最大重试次数

    # 队列配置
    task_default_queue='default',  # 默认队列
    task_queues={
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'spider': {  # 爬虫任务专用队列
            'exchange': 'spider',
            'routing_key': 'spider',
        },
        'sentiment': {  # 情感分析任务专用队列
            'exchange': 'sentiment',
            'routing_key': 'sentiment',
        },
    },

    # 路由配置
    task_routes={
        'tasks.celery_spider.*': {'queue': 'spider'},
        'tasks.celery_sentiment.*': {'queue': 'sentiment'},
    },
)

# 信号处理器
@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **extras):
    """任务开始前的处理"""
    logger.info(f"[任务开始] {task.name} | task_id={task_id} | args={args[:2] if args else 'none'}")

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """任务成功完成的处理"""
    task_name = sender.name if sender else 'unknown'
    task_id = kwargs.get('task_id', 'unknown')
    logger.info(f"[任务成功] {task_name} | task_id={task_id}")

    # 可以在这里添加指标收集
    try:
        from utils.metrics import increment_counter
        increment_counter('celery_task_success', labels={'task': task_name})
    except ImportError:
        pass

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """任务失败的处理"""
    task_name = sender.name if sender else 'unknown'
    logger.error(f"[任务失败] {task_name} | task_id={task_id} | error={exception}")

    # 可以在这里添加告警
    try:
        from utils.metrics import increment_counter
        increment_counter('celery_task_failure', labels={'task': task_name, 'error': type(exception).__name__})
    except ImportError:
        pass

# 健康检查任务（可选）
@celery_app.task(name='tasks.health_check')
def health_check_task():
    """系统健康检查任务"""
    return {
        'status': 'healthy',
        'celery': 'running',
        'timestamp': time.time()
    }

if __name__ == '__main__':
    # 本地测试启动
    celery_app.start()
